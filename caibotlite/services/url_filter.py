import os
import re
import urllib.request
from datetime import datetime, timedelta

from nonebot import logger


class UrlFilter:
    instance = None
    TLDS_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    TLDS_FILE = r"./data/tlds.txt"
    CACHE_EXPIRY = timedelta(days=1)

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(UrlFilter, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.tlds = self.load_tlds()
        self.url_pattern = self.build_url_regex()

    def download_tlds(self):
        try:
            with urllib.request.urlopen(self.TLDS_URL) as response:
                data = response.read().decode('utf-8')
            with open(self.TLDS_FILE, 'w') as file:
                file.write(data)
        except Exception as e:
            logger.error(f"TLDs下载失败: {e}")

    def is_cache_expired(self):
        if not os.path.exists(self.TLDS_FILE):
            return True
        file_time = datetime.fromtimestamp(os.path.getmtime(self.TLDS_FILE))
        return datetime.now() - file_time > self.CACHE_EXPIRY

    def load_tlds(self):
        if self.is_cache_expired():
            self.download_tlds()
        with open(self.TLDS_FILE, 'r') as file:
            tlds = [line.strip().lower() for line in file if line.strip() and not line.startswith('#')]
            # 按长度从长到短排序
        tlds.sort(key=len, reverse=True)
        return tlds

    def build_url_regex(self):
        escaped_tlds = [re.escape(tld) for tld in self.tlds]
        tld_pattern = '|'.join(escaped_tlds)
        url_pattern = rf'(https?://(?:[a-zA-Z0-9-]+\.)+(?:{tld_pattern})(?::\d+)?(?:/[^\s]*)?)|((?:[a-zA-Z0-9-]+\.)+(?:{tld_pattern})(?::\d+)?)(?=[\s,.\n]|$)'
        return re.compile(url_pattern, re.IGNORECASE)

    @classmethod
    def replace_urls(cls, replace_text):
        return cls.instance.url_pattern.sub('***', replace_text)

    @classmethod
    def has_url(cls, check_text):
        return bool(cls.instance.url_pattern.search(check_text))


UrlFilter()

if __name__ == "__main__":
    text = '''
    Visit our website at https://www.example.com or http://sub.example.org/path.
    Invalid URLs like https://example.invalid or http://test.local should not be replaced.
    terraria.inkdadwad
    terraria.ink,terraria.innknsndsk
    terraria.ink
    terraria.ink.
    terraria.ink:7777
    '''

    result = UrlFilter.replace_urls(text)
    print(result)
