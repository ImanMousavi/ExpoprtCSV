import csv
import json
from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from khayyam import JalaliDatetime
from requests.auth import HTTPBasicAuth

userId = "304794"  # <-- Change this

url = "https://app.trackingtime.co/api/v4/{0}/events".format(userId)

tow_months = datetime.now().today() + relativedelta(months=-2)

dateStartReport = '{0:%Y-%m-%d}'.format(tow_months)  # Start date
dateEndReport = '{0:%Y-%m-%d}'.format(datetime.now())  # End date

querystring = {"from": dateStartReport, "to": dateEndReport, "page": "0", "page_size": "2000"}

response = requests.get(url, auth=HTTPBasicAuth('---user---', '---pass---'), params=querystring)  # <-- Change this

data = json.loads(response.text)


class WorkClass(object):
    jDate = ""
    start = ""
    end = ""
    duration = 0
    date = 0
    total = 0


if data['response']['status'] == 200:
    timeSheet = list()

    for w in data['data']:
        wStart = datetime.strptime(w['start'], '%Y-%m-%d %H:%M:%S')
        wTimeStart = datetime.strptime(w['loc_start'], '%m/%d/%Y %I:%M:%S %p')
        wTimeEnd = datetime.strptime(w['loc_end'], '%m/%d/%Y %I:%M:%S %p')
        jDate = JalaliDatetime(wStart).strftime('%Y-%m-%d')

        work = WorkClass()
        work.jDate = jDate
        work.start = '{0:%I:%M %p}'.format(wTimeStart)
        work.end = '{0:%I:%M %p}'.format(wTimeEnd)
        work.duration = w['formated_duration']
        work.date = '{0:%Y-%m-%d}'.format(wStart)
        work.total = w['duration']

        updated = False
        if len(timeSheet) == 0:
            timeSheet.append(work)
        else:
            for idx, item in enumerate(timeSheet):
                if work.date == item.date:
                    timeSheet[idx].total = timeSheet[idx].total + work.total
                    timeSheet[idx].duration = str(timedelta(seconds=timeSheet[idx].total))
                    s = datetime.strptime(timeSheet[idx].start.split(',')[0], '%I:%M %p')
                    timeSheet[idx].end = '{0:%I:%M %p}'.format((s + timedelta(seconds=timeSheet[idx].total)))
                    updated = True
                    break
            if not updated:
                timeSheet.append(work)

    with open('export.csv', 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['jDate', 'start', 'end', 'duration', 'date', 'total'])
        for item in timeSheet:
            writer.writerow([item.jDate, item.start, item.end, item.duration, item.date, item.total])
else:
    print(data['response'])
