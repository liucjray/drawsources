import os
import requests
import datetime
import schedule
from drawsources._168 import *

url = 'https://api.api68.com/klsf/getHistoryLotteryInfo.do?date=&lotCode=10009'

db_name = os.getenv("STORAGE_PATH") + 'klsf.db'


def job():
    try:
        print('Start@' + str(datetime.datetime.now()))
        r = requests.get(url)
        j = r.json()
        data = j['result']['data']

        issues = []
        for issue in data:
            issues.append(issue['preDrawIssue'])
        # print(issues)

        codes = []
        for code in data:
            codes.append(code['preDrawCode'])
        # print(codes)

        if len(issues) == len(codes):
            data = []
            for issue in issues:
                index = issues.index(issue)
                row = {
                    'resource': '168',
                    'area': 'cq',
                    'issue': issue,
                    'code': codes[index],
                    'created_at': datetime.datetime.now()
                }
                data.append(row)
            deferred_db.init(db_name)
            IssueInfo.insert_many(data).execute()
    except ():
        print('Exception occurred.')
    finally:
        print('Finish@' + str(datetime.datetime.now()))


schedule.every(10).seconds.do(job)

while True:
    schedule.run_pending()
