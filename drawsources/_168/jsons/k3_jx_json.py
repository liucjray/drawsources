from lib.sources.Source168 import *


def get_instance():
    return Source168({
        'url': 'http://api.api68.com/lotteryJSFastThree/getJSFastThreeList.do?date=&lotCode=10007',
        'resource': '168',
        'area': 'js',
        'type': 'k3',
    })
