import sys
import requests

date_to_start_calendar = "2019-01-01"
days=60
url = "http://www.peelregion.ca/waste-scripts/when-does-it-go/nextCollectionHTML.asp?service=bm-cr-mon-b&days="+str(days)+"&date="+date_to_start_calendar+"&hidden=0"

my_referer = sys.argv[1] # This is the query url with the Address, generated from peelregion website

s = requests.Session()
s.headers.update({'referer': my_referer})
html = s.get(url)
print html.content
with open('Waste.html', 'w') as my_file:
    my_file.writelines(html.content)
