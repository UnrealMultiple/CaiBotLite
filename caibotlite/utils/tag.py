import json
import re

from nonebot import logger

_item_info = {}
_prefix_info = {}

def _init():
    global _item_info, _prefix_info
    with open("assets/terraria_data/item_id.json", encoding='utf-8', errors='ignore') as fp:
        item_json = json.loads(fp.read())

    with open("assets/terraria_data/prefix_id.json", encoding='utf-8', errors='ignore') as fp:
        prefix_json = json.loads(fp.read())

    _item_info = {item['ItemId']: item for item in item_json}
    _prefix_info = {prefix['PrefixId']: prefix for prefix in prefix_json}
    logger.success("[tag]物品、前缀已缓存!")

_init()

def remove_color_tag(text: str):
    find = re.findall(r"\[c?/[0-9a-fA-F]{6}:(.*?)]", text)
    for i in find:
        text = re.sub(r"\[c?/[0-9a-fA-F]{6}:(.*?)]", i, text, 1)
    return text


def replace_item_tag(text: str):

    find = re.findall(r"\[i?(?:/s(\d{1,4}))?(?:/p(\d{1,3}))?:(-?\d{1,4})]", text)
    for i in find:
        try:
            item = "["
            item_id = int(i[2])
            num = i[0]
            prefix = i[1]
            if prefix != "":
                item = item + _prefix_info[prefix + 1]['Name'] + "的 "
            item = item + _item_info[item_id]['Name']
            if num != "" and num != "1":
                item = item + f"({num})"
            item = item + "]"
            text = re.sub(r"\[i?(?:/s(\d{1,4}))?(?:/p(\d{1,3}))?:(-?\d{1,4})]", item, text, 1)
        except IndexError:
            logger.error("错误物品Tag:" + str(i))

    return text

