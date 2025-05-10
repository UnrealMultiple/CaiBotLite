import os
import re
import urllib.request
from datetime import datetime, timedelta


class UrlHandler:
    instance = None  # 单例实例

    # IANA 顶级域名列表 URL
    TLDS_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    # 本地缓存文件路径
    TLDS_FILE = "tlds.txt"
    # 缓存文件的有效期（1天）
    CACHE_EXPIRY = timedelta(days=1)

    def __new__(cls, *args, **kwargs):
        # 实现单例模式
        if cls.instance is None:
            cls.instance = super(UrlHandler, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.tlds = self.load_tlds()
        self.url_pattern = self.build_url_regex()

    # 下载最新的顶级域名列表
    def download_tlds(self):
        try:
            with urllib.request.urlopen(self.TLDS_URL) as response:
                data = response.read().decode('utf-8')
            with open(self.TLDS_FILE, 'w') as file:
                file.write(data)
        except Exception as e:
            print(f"TLDs下载失败: {e}")

    # 检查缓存文件是否过期
    def is_cache_expired(self):
        if not os.path.exists(self.TLDS_FILE):
            return True
        file_time = datetime.fromtimestamp(os.path.getmtime(self.TLDS_FILE))
        return datetime.now() - file_time > self.CACHE_EXPIRY

    # 加载顶级域名列表
    def load_tlds(self):
        if self.is_cache_expired():
            self.download_tlds()
        with open(self.TLDS_FILE, 'r') as file:
            tlds = [line.strip().lower() for line in file if line.strip() and not line.startswith('#')]
            # 按长度从长到短排序
        tlds.sort(key=len, reverse=True)
        return tlds

    # 构建正则表达式
    def build_url_regex(self):
        # 转义顶级域名中的点（.），并构建正则表达式
        escaped_tlds = [re.escape(tld) for tld in self.tlds]
        tld_pattern = '|'.join(escaped_tlds)
        # 匹配完整 URL 的正则表达式
        url_pattern = rf'(https?://(?:[a-zA-Z0-9-]+\.)+(?:{tld_pattern})(?::\d+)?(?:/[^\s]*)?)|((?:[a-zA-Z0-9-]+\.)+(?:{tld_pattern})(?::\d+)?)(?=[\s,.\n]|$)'
        return re.compile(url_pattern, re.IGNORECASE)

    @classmethod
    def replace_urls(cls, replace_text):
        return cls.instance.url_pattern.sub('***', replace_text)

    @classmethod
    def has_url(cls, replace_text):
        return cls.instance.url_pattern.sub('***', replace_text)

    @classmethod
    def is_match(cls,check_text):
        return bool(cls.instance.url_pattern.search(check_text))

UrlHandler()

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

    result = UrlHandler.replace_urls(text)
    print(result)