import datetime
import requests
from addict import Dict
from lib.IssueInfo import *
from bs4 import BeautifulSoup
import re


class SourceApiLottery:
    __domain__ = 'http://www.apilottery.com/'

    font_map_code = {
        '\ue342': 0,
        '\ue512': 1,
        '\ue808': 2,
        '\ue456': 3,
        '\ue542': 4,
        '\ue338': 5,
        '\ue293': 6,
        '\ue831': 7,
        '\ue098': 8,
        '\ue132': 9,
    }
    font2_map_code = {
        '\ue831': 0,
        '\ue338': 1,
        '\ue808': 2,
        '\ue456': 3,
        '\ue542': 4,
        '\ue132': 5,
        '\ue293': 6,
        '\ue098': 7,
        '\ue342': 8,
        '\ue512': 9,
    }

    def __init__(self, settings):
        self.settings = Dict(settings)
        self.data = Dict()
        self.codes = []
        self.issues = []
        self.infos = []
        self.draw_ats = []

    def clean(self):
        self.data = Dict()
        self.codes = []
        self.issues = []
        self.infos = []
        self.draw_ats = []

    def parse(self):
        url = self.__domain__ + self.settings.url
        r = requests.get(url, headers=self.settings.headers).json()
        d = Dict(r)
        self.data = d.data

    def get_font_map_code(self, soup):
        matches = re.findall(r'/(font\d*)/fontello.eot', soup.select('style')[0].text)
        print(matches[0])
        if matches[0] == 'font':
            return self.font_map_code
        elif matches[0] == 'font2':
            return self.font2_map_code
        else:
            print('font map {} not found.'.format(matches[0]))

    def parse_html(self):
        url = self.__domain__ + self.settings.url
        print(url)

        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')

        font_map_code = self.get_font_map_code(soup)
        trs = soup.select('.layui-table > tbody > tr')

        i = 0
        for tr in trs:
            i = i + 1
            issue = tr.select('td')[0].text
            self.issues.append(issue)

            codes = []
            for code in tr.select('td > .code'):
                codes.append(self.decode_code(font_map_code, code.text))
            code = ",".join(codes)
            self.codes.append(code)

            draw_at = tr.select('td')[2].text
            self.draw_ats.append(draw_at)

        # print(self.issues)
        # print(self.codes)
        # print(self.draw_ats)
        # exit()

    def decode_code(self, code_map, code):
        codes = []
        for char in list(code):
            codes.append(str(code_map[char]))
        code = "".join(codes)
        return code

    def get_codes(self):
        return self.codes

    def get_issues(self):
        return self.issues

    def get_draw_ats(self):
        return self.draw_ats

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
                    'draw_at': self.draw_ats[index],
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
        return len(self.codes) == len(self.issues) \
               and len(self.codes) > 0 \
               and len(self.issues) > 0

    def handle(self):
        print('Start: %s' % datetime.datetime.now())
        self.clean()
        self.parse_html()
        self.get_issues()
        self.get_codes()
        self.get_draw_ats()
        self.write()
        print('End: %s' % datetime.datetime.now())
