import os
import random


class SourceBase:

    def get_http_proxy(self):
        s = os.getenv("STORAGE_PATH")
        with open(s + 'http_proxy.txt') as f:
            proxy = f.read().splitlines()
        return proxy

    def get_https_proxy(self):
        s = os.getenv("STORAGE_PATH")
        with open(s + 'https_proxy.txt') as f:
            proxy = f.read().splitlines()
        return proxy

    def get_random_https_proxy(self):
        https_proxies = self.get_https_proxy()
        proxy = random.choice(https_proxies)
        return proxy

    def get_random_http_proxy(self):
        http_proxies = self.get_http_proxy()
        proxy = random.choice(http_proxies)
        return proxy

    def get_proxy_by_country(self, country):
        s = os.getenv("STORAGE_PATH")
        file_name = '{}{}_{}.txt'.format(s, 'http_proxy', country)
        with open(file_name) as f:
            proxy = f.read().splitlines()
        return proxy

    def get_random_proxy(self, proxies):
        proxy = random.choice(proxies)
        return proxy
