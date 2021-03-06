from flask import Flask, render_template, request, send_file
from datetime import datetime
from ics import Calendar, Event
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup
import StringIO
import unicodedata
import re

YEAR = str(datetime.now().year)

def rreplace(string_to_replace_on, old, new, times):
    """
    Serach reverse and replace last occurrence
    """
    li = string_to_replace_on.rsplit(old, times)
    return new.join(li)

def generate_ics_from_data(content):
    """
    Parameter content will be the raw_data parsed in text form, convert that and return in ics format
    """
    dates_dictionary = OrderedDict() # Dictionary with Dates and number of entries for each day
    dates_dictionary_formatted = OrderedDict() # Same dictionary formatted dates
    description = list() # Store the description of events happening each day
    content = content.split('\n') # Split into lines and return a list
    file_data = filter(None, content) # remove empty items
    # Parse data into Dates and events
    date = ''
    event_num = 0
    for x in file_data :
        # If the last char of a line is a number it is date
        if x[-1:].isnumeric():
            date = x
            event_num = 0
            dates_dictionary.update({date:event_num})
        # If the last word is today , that also means it's a date
        elif x[-7:] == '- Today':
            date = x[:-7] # String the today part before appending
            event_num = 0
            dates_dictionary.update({date:event_num})
        else:
            event_num += 1
            dates_dictionary.update({date:event_num})
            description.append(x) # This is a waste type, not a date
    # Convert dates into needed format
    # https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    for x, y in dates_dictionary.items():
        date = datetime.strptime(x+' '+YEAR, '%A, %B %d %Y') # Strip date
        formatted_date = date.strftime('%Y%m%d') # Format date from stripped date
        dates_dictionary_formatted.update({formatted_date:y})
    # Format data into ics file
    c = Calendar()
    description_for_the_day = '' # Initialize empty description so it can be appended
    for x, y in dates_dictionary_formatted.items():
        e = Event()
        for i in range(y):
            description_for_the_day += description.pop(0)
            description_for_the_day += ', '
        description_for_the_day = description_for_the_day[:-2] # Remove the comma at the end
        description_for_the_day = rreplace(description_for_the_day, ',', ' and', 1) # Replace last comma with an and
        e.begin = x+' 00:00:00'
        e.end = x+' 12:00:00'
        e.make_all_day() # Make the event all day
        e.description = "Waste Collection day"
        e.name = description_for_the_day
        c.events.add(e)
        description_for_the_day = '' # Reset this
        del e # Delete event content after appending to the calendar
    return c # Return the calendar data

def parse_data_from_url(my_referer):
    """
    my_referer is the query url with the Address, generated from
    peelregion website entered by the people and return text data in a
    string
    """
    date_to_start_calendar = YEAR+'-01-01' # Make something like 2019-01-01
    days=400 # Max number of days
    # Find the service id
    s = requests.Session()
    html = None
    try:
        html = s.get(my_referer) # Get raw html data
    except requests.exceptions.RequestException as e:
        # Failed to retrieve, so pass on with the default id boiii
        return False, 'Did you enter a url?'
    if html != None:
        soup = BeautifulSoup(html.content,"html.parser")
        serive_id = re.search('currentService\ =\ \"(.+)\"',soup.get_text())
        if serive_id != None:
            serive_id = serive_id.groups()[0]
        else:
            # User probably a wrong url
            return False, 'Wrong url!'
    del s
    url = "http://www.peelregion.ca/waste-scripts/when-does-it-go/nextCollectionHTML.asp?service="+serive_id+"&days="+str(days)+"&date="+date_to_start_calendar+"&hidden=0"
    s = requests.Session() # new session
    s.headers.update({'referer': my_referer})
    try:
        html = s.get(url) # Get raw html data
    except requests.exceptions.RequestException as e:
        return False, 'Failed to collect data!' # Failed tp retrieve
    if html != None:
        soup = BeautifulSoup(html.content,"html.parser")
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip out style and script tags
        return True, soup.get_text() # Get remaining text data
    else:
        return False, 'Data retrieved was malformed!' # Failed to retrieve
        

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Serves index.html
    """
    url = None
    if request.method == 'POST' and 'url' in request.form:
        url = request.form['url']
        strIO = StringIO.StringIO()
        success, raw_data_or_error = parse_data_from_url(url)
        if success :
            calender_data = generate_ics_from_data(raw_data_or_error)
            strIO.write(str(calender_data))
            strIO.seek(0)
            return send_file(strIO, attachment_filename="Waste disposal calendar.ics",as_attachment=True)
        else:
            return render_template('index.html', error=raw_data_or_error)
    else: # GET
        return render_template('index.html')

if __name__ == '__main__':
    app.run()
