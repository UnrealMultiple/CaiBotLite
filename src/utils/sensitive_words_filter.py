import json
import ahocorasick
from functools import lru_cache

from src.utils.url_handler import UrlHandler


class SensitiveWordsFilter:
    automaton = None
    _instance = None

    def __new__(cls, file_path):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # 初始化AC自动机
            cls.automaton = ahocorasick.Automaton()
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            words = sorted(data['words'], key=lambda x: -len(x))
            for word in words:
                cls.automaton.add_word(word, (len(word), word))
            cls.automaton.make_automaton()
        return cls._instance

    @classmethod
    @lru_cache(maxsize=10000)
    def check(cls, text):
        """类方法：敏感词检测"""

        if UrlHandler.is_match(text):
            return True

        for end, (length, word) in cls.automaton.iter(text):
            start = end - length + 1
            if text[start:end + 1] == word:
                return True
        return False

    @classmethod
    def replace(cls, text):
        """类方法：替换敏感词"""

        # 替换URL

        text = UrlHandler.replace_urls(text)

        text_list = list(text)
        matches = []

        # 获取所有匹配位置
        for end, (length, word) in cls.automaton.iter(text):
            start = end - length + 1
            if text[start:end + 1] == word:
                matches.append((start, end))

        # 合并重叠区间（关键算法）
        merged = []
        for start, end in sorted(matches, key=lambda x: (x[0], -x[1])):
            if not merged or start > merged[-1][1]:
                merged.append((start, end))
            else:
                prev_start, prev_end = merged[-1]
                merged[-1] = (prev_start, max(prev_end, end))

        # 批量替换星号
        for start, end in merged:
            text_list[start:end + 1] = '*' * (end - start + 1)

        return ''.join(text_list)


SensitiveWordsFilter('Sensitive.json')


