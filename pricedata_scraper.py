import requests
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import requests, urllib3

h = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    }
sesh = requests.Session()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dategen = (x for x in pd.date_range(start="1/1/2015", end='1/1/2020').to_pydatetime())

prevscrapeddates = os.listdir("fruitprices_raw")
prevscrapeddates = [d.split("_")[1] for d in prevscrapeddates]

def dailyurl(dateobj):
    y = int(datetime.strftime(dateobj, "%Y")) - 1911
    md = datetime.strftime(dateobj, ".%m.%d")
    url = "https://data.coa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx?$top=1000&$skip=000&StartDate=" + str(y) + md + "&Market=%E5%8F%B0%E5%8C%97%E5%B8%82%E5%A0%B4"
    return(url)

for date in dategen:
    datestring = datetime.strftime(date, "%Y-%m-%d")
    if datestring in prevscrapeddates:
        continue
    page = sesh.get(dailyurl(date), verify=False, headers=h)
    page = page.content.decode('utf8')
    entries = len(json.loads(page))
    print(f"Date: {datestring}, Entries: {entries}")
    with open(f"fruitprices_raw/fruitprice_{datestring}_raw.json", "w") as file:
        file.write(page)
