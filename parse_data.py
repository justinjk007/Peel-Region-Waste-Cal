import sys
import requests
from bs4 import BeautifulSoup


date_to_start_calendar = "2019-01-01"
days=60
url = "http://www.peelregion.ca/waste-scripts/when-does-it-go/nextCollectionHTML.asp?service=bm-cr-mon-b&days="+str(days)+"&date="+date_to_start_calendar+"&hidden=0"

my_referer = sys.argv[1] # This is the query url with the Address, generated from peelregion website

s = requests.Session()
s.headers.update({'referer': my_referer})
html = s.get(url)

soup = BeautifulSoup(html.content,"html.parser")
# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()    # rip it out
# Get remaining text data
text = soup.get_text()
with open('Waste.txt', 'w') as my_file:
    my_file.writelines(text)
