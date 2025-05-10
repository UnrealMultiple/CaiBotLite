import base64
import io
import json
from fuzzywuzzy import fuzz

from nonebot.log import logger
from nonebot.adapters.qq import MessageSegment
from common.bag_png_helper import image_cache


with open("terraria_id/item_id.json", encoding='utf-8', errors='ignore') as fp:
    items = json.loads(fp.read())

with open("terraria_id/prefix_id.json", encoding='utf-8', errors='ignore') as fp:
    prefixes = json.loads(fp.read())

with open("terraria_id/project_id.json", encoding='utf-8', errors='ignore') as fp:
    projects = json.loads(fp.read())

with open("terraria_id/npc_id.json", encoding='utf-8', errors='ignore') as fp:
    NPCs = json.loads(fp.read())

with open("terraria_id/buff_id.json", encoding='utf-8', errors='ignore') as fp:
    buffs = json.loads(fp.read())

logger.success("[terraria_id]物品、前缀、生物、Buff、弹幕已缓存!")


def get_item_info_string(item) -> (str, MessageSegment):
    info = [f"物品名: {item['Name']}", f"ID: {item['ItemId']}", f"最大堆叠: {item['MaxStack']}"]

    if item['Damage'] != -1:
        info.append(f"伤害: {item['Damage']}")

    monetary_value = item['MonetaryValue']

    if any(value != 0 for value in monetary_value.values()):
        monetary_info = (f"钱币: {str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                         f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                         f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                         f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}")
        info.append(monetary_info)
    else:
        info.append("钱币: 无价")

    if item['Description'] != "":
        info.append(f"{item['Description']}", )

    if item['Alias']:
        info.append("别名: " + ",".join(item['Alias']))

    byte_arr = io.BytesIO()
    image_cache[f"item_{item['ItemId']}"].save(byte_arr, format='PNG')
    return "\n".join(info), MessageSegment.file_image(byte_arr)


def get_npc_info_string(item):
    info = [f"生物名: {item['Name']}", f"ID: {item['NpcId']}", f"生命值: {item['LifeMax']}"]

    if item['Damage'] != -1:
        info.append(f"伤害: {item['Damage']}")

    monetary_value = item['MonetaryValue']

    if any(value != 0 for value in monetary_value.values()):
        monetary_info = (f"钱币: {str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                         f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                         f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                         f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}")
        info.append(monetary_info)
    else:
        info.append("钱币: 无价")

    if item['Description'] != "":
        info.append(f"{item['Description']}")

    if item['Alias']:
        info.append("别名: " + ",".join(item['Alias']))

    return "\n".join(info)


def get_project_info_string(item):
    info = [f"弹幕名: {item['Name']}", f"ID: {item['ProjId']}", f"AI类型: {item['AiStyle']}",
            f"友方: {item['Friendly']}"]

    if item['Alias']:
        info.append("别名: " + ",".join(item['Alias']))

    return "\n".join(info)


def get_buff_info_string(item) -> (str, MessageSegment):
    info = [f"增益名: {item['Name']}", f"ID: {item['BuffId']}"]
    if item['Description'] != "":
        info.append(f"{item['Description']}")

    if item['Alias']:
        info.append("别名: " + ",".join(item['Alias']))
    byte_arr = io.BytesIO()
    image_cache[f"buff_{item['BuffId']}"].save(byte_arr, format='PNG')
    return "\n".join(info), MessageSegment.file_image(byte_arr)


def get_prefix_info_string(item):
    info = [f"修饰语: {item['Name']}", f"ID: {item['PrefixId']}"]

    if item['Alias']:
        info.append("别名: " + ",".join(item['Alias']))

    return "\n".join(info)


def enhanced_search(query, dataset, id_field, name_field, alias_field='Alias'):
    """增强版搜索算法（支持别名搜索）"""
    # 尝试ID匹配
    try:
        query_id = int(query)
        for item in dataset:
            if item[id_field] == query_id:
                return [item]
    except ValueError:
        pass

    # 多维度搜索
    results = []
    query_lower = query.lower()

    for item in dataset:
        name = item[name_field]
        aliases = item[alias_field]
        all_names = [name] + aliases


        best_score = 0

        for current_name in all_names:
            if not current_name:  # 跳过空名称
                continue

            name_lower = current_name.lower()

            # 1. 完全匹配（最高优先级）
            if current_name == query:
                return [item]

            # 2. 开头匹配（次高优先级）
            if current_name.startswith(query):
                best_score = max(best_score, 100)
                continue

            # 3. 包含匹配
            if query in current_name:
                best_score = max(best_score, 90)
                continue


            # 6. 模糊匹配
            ratio = fuzz.ratio(query_lower, name_lower)
            if ratio > 90:  # 降低阈值以增加召回率
                best_score = max(best_score, ratio)

        # 如果找到任何匹配，则添加到结果
        if best_score > 0:
            results.append((item, best_score))

    # 按匹配度排序
    results.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in results]


def get_search_result(query, dataset, id_field, name_field, info_func):
    """通用搜索处理函数"""
    matched = enhanced_search(query, dataset, id_field, name_field)

    if not matched:
        return "啥东西都没找到哦!"
    elif len(matched) == 1:
        return info_func(matched[0])
    else:
        limit = min(80, len(matched))
        return f"找到{len(matched)}个匹配结果{f'(已展示{limit}个)' if limit!=len(matched) else ''}: " + ", ".join(
            [f'{item[name_field]}({item[id_field]})' for item in matched[:limit]]
        ),None


def get_item_by_name_or_id(query):
    return get_search_result(query, items, "ItemId", "Name", get_item_info_string)


def get_npc_by_name_or_id(query):
    return get_search_result(query, NPCs, "NpcId", "Name", get_npc_info_string)


def get_project_by_name_or_id(query):
    return get_search_result(query, projects, "ProjId", "Name", get_project_info_string)


def get_buff_by_name_or_id(query):
    return get_search_result(query, buffs, "BuffId", "Name", get_buff_info_string)


def get_prefix_by_name_or_id(query):
    return get_search_result(query, prefixes, "PrefixId", "Name", get_prefix_info_string)