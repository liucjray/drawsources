import time
from datetime import timedelta, datetime
from lib.sources.SourceApiLottery import *

for x in range(0, 30):
    date = datetime.datetime.strftime(datetime.datetime.now() - timedelta(1) - timedelta(x), '%Y-%m-%d')
    print("############### {} #################".format(date))
    s = SourceApiLottery({
        'resource': 'apilottery',
        'type': 'ssc',
        'area': 'hanoi',
        'url': 'his/hn5fc/{}'.format(date)
    })
    s.handle()
    time.sleep(1)
