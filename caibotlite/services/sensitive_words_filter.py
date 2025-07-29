import json

import ahocorasick


class SensitiveWordsFilter:
    automaton = None
    _instance = None

    def __new__(cls, file_path):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls.automaton = ahocorasick.Automaton()
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            words = sorted(data['words'], key=lambda x: -len(x))
            for word in words:
                cls.automaton.add_word(word, (len(word), word))
            cls.automaton.make_automaton()
        return cls._instance

    @classmethod
    def has_sensitive(cls, text):
        """类方法：敏感词检测"""
        for end, (length, word) in cls.automaton.iter(text):
            start = end - length + 1
            if text[start:end + 1] == word:
                return True
        return False

    @classmethod
    def replace(cls, text):
        """类方法：替换敏感词"""
        text_list = list(text)
        matches = []

        for end, (length, word) in cls.automaton.iter(text):
            start = end - length + 1
            if text[start:end + 1] == word:
                matches.append((start, end))

        merged = []
        for start, end in sorted(matches, key=lambda x: (x[0], -x[1])):
            if not merged or start > merged[-1][1]:
                merged.append((start, end))
            else:
                prev_start, prev_end = merged[-1]
                merged[-1] = (prev_start, max(prev_end, end))

        for start, end in merged:
            text_list[start:end + 1] = '*' * (end - start + 1)

        return ''.join(text_list)


SensitiveWordsFilter(r'./data/Sensitive.json')
