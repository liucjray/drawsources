import datetime
import json

import requests
from addict import Dict
from lib.IssueInfo import *


class SourceMacauJC:
    __domain__ = 'https://macaujc.com/'

    def __init__(self, settings):
        self.settings = Dict(settings)
        self.data = Dict()
        self.codes = []
        self.issues = []
        self.draw_at = []

    def clean(self):
        self.data = Dict()
        self.codes = []
        self.issues = []
        self.draw_at = []

    def parse(self):
        url = self.__domain__ + self.settings.url

        raw_data = json.dumps(self.settings.raw_data)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, data=raw_data, headers=headers)
        d = json.loads(r.text)
        self.data = d['data']

        issues = []
        codes = []
        draw_at = []

        for row in self.data:
            # 取得 issue
            issues.append(row['issue'])
            codes.append(row['openCode'])
            draw_at.append(row['openTime'])

        self.issues = issues
        self.codes = codes
        self.draw_at = draw_at

    def get_issues(self):
        return self.issues

    def get_codes(self):
        return self.codes

    def get_draw_at(self):
        return self.draw_at

    def write(self):
        if self.validate():
            prepare_insert = []
            for issue in self.issues:
                index = self.issues.index(issue)
                row = {
                    'resource': self.settings.resource,
                    'type': self.settings.type,
                    'area': self.settings.area,
                    'issue': issue,
                    'code': self.codes[index],
                    'draw_at': self.draw_at[index],
                    'created_at': str(datetime.datetime.now())
                }
                prepare_insert.append(row)

            # 切分一百組資料為一個 chunk 避免資料量大無法寫入問題
            chunks = [prepare_insert[x:x + 100] for x in range(0, len(prepare_insert), 100)]

            for chunk in chunks:
                IssueInfo.insert_many(chunk).on_conflict('ignore').execute()
        else:
            print('Validate Error! resource: {} type: {} area: {}'.format(
                self.settings.resource,
                self.settings.type,
                self.settings.area))

    def validate(self):
        print(self.codes, self.issues)
        return len(self.codes) == len(self.issues) \
               and len(self.codes) > 0 \
               and len(self.issues) > 0

    def handle(self):
        print('Start: %s' % datetime.datetime.now())
        self.clean()
        self.parse()
        self.get_issues()
        self.get_codes()
        self.write()
        print('End: %s' % datetime.datetime.now())
