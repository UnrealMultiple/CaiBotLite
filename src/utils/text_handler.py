﻿import html
import json
import re

from nonebot import logger

with open("assets/terraria_data/item_id.json", encoding='utf-8', errors='ignore') as fp:
    item_json = json.loads(fp.read())

with open("assets/terraria_data/prefix_id.json", encoding='utf-8', errors='ignore') as fp:
    prefix_json = json.loads(fp.read())

item_info = {item['ItemId']: item for item in item_json}
prefix_info = {prefix['PrefixId']: prefix for prefix in prefix_json}

logger.success("[TextHandle]物品、前缀已缓存!")


class TextHandle:
    @staticmethod
    def check_name(name: str):
        pattern = re.compile(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$')
        if pattern.match(name):
            return True
        else:
            return False

    @staticmethod
    def color(text: str):
        find = re.findall("\[c?\/[0-9a-fA-F]{6}:(.*?)\]", text)
        for i in find:
            text = re.sub("\[c?\/[0-9a-fA-F]{6}:(.*?)\]", i, text, 1)
        return text

    @staticmethod
    def item(text: str):

        find = re.findall("\[i?(?:\/s(\d{1,4}))?(?:\/p(\d{1,3}))?:(-?\d{1,4})\]", text)
        for i in find:
            try:
                item = "["
                item_id = int(i[2])
                num = i[0]
                prefix = i[1]
                if prefix != "":
                    item = item + prefix_info[prefix + 1]['Name'] + "的 "
                item = item + item_info[item_id]['Name']
                if num != "" and num != "1":
                    item = item + f"({num})"
                item = item + "]"
                text = re.sub("\[i?(?:\/s(\d{1,4}))?(?:\/p(\d{1,3}))?:(-?\d{1,4})\]", item, text, 1)
            except IndexError:
                logger.error("错误物品Tag:" + str(i))

        return text

    @staticmethod
    def all(text: str):
        return TextHandle.item(TextHandle.color(text))

    @staticmethod
    def html_decode(text: str):
        return html.unescape(text)

    @staticmethod
    def add_line_break(text: str, n: int) -> str:
        lines = [text[i:i + n] for i in range(0, len(text), n)]
        return "\n".join(lines)
