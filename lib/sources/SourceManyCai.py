import datetime
import requests
from addict import Dict
from lib.IssueInfo import *
from pymongo import MongoClient


class SourceManyCai:
    __domain__ = 'http://www.manycai365.com/'

    def __init__(self, settings):
        self.settings = Dict(settings)
        self.data = Dict()
        self.codes = []
        self.issues = []
        self.infos = []
        self.draw_at = []
        self.prepare_insert_rows = []

    def clean(self):
        self.data = Dict()
        self.codes = []
        self.issues = []
        self.infos = []
        self.draw_at = []
        self.prepare_insert_rows = []

    def parse(self):
        url = self.__domain__ + self.settings.uri

        header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.__domain__,
            "X-Requested-With": "XMLHttpRequest"
        }
        form = {
            'lotterycode': 'HN300',
            'lotteryname': 'HN300',
            'page': '1',
        }
        r = requests.post(url, data=form, headers=header).json()

        d = Dict(r)
        self.data = d.data

    def get_codes(self):
        for row in self.data:
            self.codes.append(row.code)

    def get_issues(self):
        for row in self.data:
            self.issues.append(row.issue)

    def get_draw_ats(self):
        for row in self.data:
            self.draw_at.append(row.opendate)

    def write(self):
        if self.validate():
            self.write_prepare()
            self.write_sqlite3()
            # self.write_mongo()
        else:
            print('Validate Error! resource: {} type: {} area: {}'.format(
                self.settings.resource,
                self.settings.type,
                self.settings.area))

    def write_prepare(self):
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
            self.prepare_insert_rows.append(row)

    def write_sqlite3(self):
        # 切分一百組資料為一個 chunk 避免資料量大無法寫入問題
        prepare_insert = self.prepare_insert_rows
        chunks = [prepare_insert[x:x + 100] for x in range(0, len(prepare_insert), 100)]

        for chunk in chunks:
            IssueInfo.insert_many(chunk).on_conflict('ignore').execute()

    def write_mongo(self):
        client = MongoClient(os.getenv("MONGODB_ATLAS_CONNECTION"))
        mongodb_atlas = client.get_database(os.getenv("MONGODB_ATLAS_DB"))
        issue_info = mongodb_atlas.issue_info

        # 切分一百組資料為一個 chunk 避免資料量大無法寫入問題
        prepare_insert = self.prepare_insert_rows
        chunks = [prepare_insert[x:x + 100] for x in range(0, len(prepare_insert), 100)]

        for chunk in chunks:
            try:
                # ordered=False 可於 unique index insert 時跳例外
                issue_info.insert_many(chunk, ordered=False)
            except Exception:
                pass

    def validate(self):
        return len(self.codes) == len(self.issues) \
               and len(self.codes) > 0 \
               and len(self.issues) > 0

    def handle(self):
        print('Start: %s' % datetime.datetime.now())
        self.clean()
        self.parse()
        self.get_issues()
        self.get_codes()
        self.get_draw_ats()
        self.write()
        print('End: %s' % datetime.datetime.now())
