import base64
import json
from datetime import datetime
import pandas
from dateutil.relativedelta import relativedelta
from khayyam import *
from pip._vendor import requests

url = "https://app.trackingtime.co/api/v4/251834/events"

tow_months = datetime.now().today() + relativedelta(months=-2)
dateStartReport = '{0:%Y-%m-%d}'.format(tow_months)
dateEndReport = '{0:%Y-%m-%d}'.format(datetime.now())
userId = "304794"

usrPass = '%s:%s' % ('username', 'password')
base64string = base64.standard_b64encode(usrPass.encode('utf-8'))

headers = {
    'Authorization': "Basic %s" % base64string.decode('utf-8')
}

querystring = {"from": dateStartReport, "to": dateEndReport, "filter": "USER", "id": userId, "page": "0",
               "page_size": "2000"}

response = requests.request("GET", url, headers=headers, params=querystring)

data = json.loads(response.text)
if data['response']['status'] == 200:
    timeSheet = []

    for w in data['data']:
        wStart = datetime.strptime(w['start'], '%Y-%m-%d %H:%M:%S')
        wTimeStart = datetime.strptime(w['loc_start'], '%m/%d/%Y %I:%M:%S %p')
        wTimeEnd = datetime.strptime(w['loc_end'], '%m/%d/%Y %I:%M:%S %p')
        jDate = JalaliDatetime(wStart).strftime('%Y-%m-%d')

        work = [
            # w['id'],
            jDate,
            '{0:%I:%M %p}'.format(wTimeStart),
            '{0:%I:%M %p}'.format(wTimeEnd),
            w['formated_duration'],
            '{0:%Y-%m-%d}'.format(wStart),
            w['duration'],
        ]
        timeSheet.append(work)

    column = ['jDate', 'start', 'end', 'duration', 'date', 'total (second)']

    df = pandas.DataFrame(timeSheet, columns=['jDate', 'start', 'end', 'duration', 'date', 'time'])
    df.to_csv('timeSheet.csv', index=False)

else:
    print(data['response'])
