from flask import Flask, render_template, request, send_file
from datetime import datetime
from ics import Calendar, Event
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup
import StringIO

def rreplace(string, old, new, times):
    """
    Serach reverse and replace last occurrence
    String = main string
    old = to be replaced
    new = replaced with
    times = how many replacements from the back
    """
    li = string.rsplit(old, times)
    return new.join(li)

def generate_ics_from_data(content):
    """
    Parameter content will be the raw_data parsed in text form, convert that and return in ics format
    """
    dates_dictionary = OrderedDict() # Dictionary with Dates and number of entries for each day
    dates_dictionary_formatted = OrderedDict() # Same dictionary formatted dates
    description = list() # Store the description of events happening each day
    YEAR = '2019'
    content = [x.strip() for x in content] # Remove whitespace and newline
    file_data = filter(None, content) # remove empty items
    # Parse data into Dates and events
    date = ''
    event_num = 0
    for x in file_data :
        # If the last char of a line is a number it is date
        x_code = unicode(x, 'utf-8')
        if x_code[-1:].isnumeric():
            date = x
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
        e.name = "Waste Collection day"
        for i in range(y):
            description_for_the_day += description.pop(0)
            description_for_the_day += ', '
        description_for_the_day = description_for_the_day[:-2] # Remove the comma at the end
        description_for_the_day = rreplace(description_for_the_day, ',', ' and', 1) # Replace last comma with an and
        e.begin = x+' 00:00:00'
        e.end = x+' 12:00:00'
        e.make_all_day() # Make the event all day
        e.description = description_for_the_day
        c.events.add(e)
        description_for_the_day = '' # Reset this
        del e # Delete event content after appending to the calendar
    # Write data into ics file
    # with open('Waste disposal calendar.ics', 'w') as my_file:
    #     my_file.writelines(c)

def parse_data_from_url(my_referer):
    """
    my_referer is the query url with the Address, generated from
    peelregion website entered by the people and return text data in a
    string
    """
    date_to_start_calendar = "2019-01-01"
    days=60
    url = "http://www.peelregion.ca/waste-scripts/when-does-it-go/nextCollectionHTML.asp?service=bm-cr-mon-b&days="+str(days)+"&date="+date_to_start_calendar+"&hidden=0"
    s = requests.Session()
    s.headers.update({'referer': my_referer})
    html = s.get(url) # Get raw html data
    soup = BeautifulSoup(html.content,"html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip out style and script tags
    text = soup.get_text() # Get remaining text data
    # with open('Waste.txt', 'w') as my_file:
    #     my_file.writelines(text)
    return text

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    if request.method == 'POST' and 'name' in request.form:
        name = request.form['name']
    strIO = StringIO.StringIO()
    strIO.write('Hello from Dan Jacob and Stephane Wirtel !')
    strIO.seek(0)
    # return send_file(strIO, attachment_filename="testing.txt",as_attachment=True)
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
