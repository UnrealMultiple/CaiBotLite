import io
import json

from fuzzywuzzy import fuzz
from nonebot.adapters.qq import MessageSegment
from nonebot.log import logger

from caibotlite.services.lookbag import LookBag


class TerrariaSearch:
    items = []
    prefixes = []
    projectiles = []
    NPCs = []
    buffs = []
    configs = []
    permissions = []

    @classmethod
    def init_search(cls):
        with open("assets/terraria_data/item_id.json", encoding='utf-8', errors='ignore') as fp:
            cls.items = json.loads(fp.read())

        with open("assets/terraria_data/prefix_id.json", encoding='utf-8', errors='ignore') as fp:
            cls.prefixes = json.loads(fp.read())

        with open("assets/terraria_data/project_id.json", encoding='utf-8', errors='ignore') as fp:
            cls.projectiles = json.loads(fp.read())

        with open("assets/terraria_data/npc_id.json", encoding='utf-8', errors='ignore') as fp:
            cls.NPCs = json.loads(fp.read())

        with open("assets/terraria_data/buff_id.json", encoding='utf-8', errors='ignore') as fp:
            cls.buffs = json.loads(fp.read())

        with open("assets/terraria_data/config_id.json", encoding='utf-8', errors='ignore') as fp:
            cls.configs = json.loads(fp.read())

        with open("assets/terraria_data/permission_id.json", encoding='utf-8', errors='ignore') as fp:
            cls.permissions = json.loads(fp.read())

    logger.success("[terraria_search]物品、前缀、生物、buffs、弹幕已缓存!")

    @classmethod
    def _get_item_info_string(cls, item):
        info = [f"物品名: {item['Name']}", f"ID: {item['ItemId']}", f"最大堆叠: {item['MaxStack']}"]

        if item['WeaponType']:
            info.append(f"武器类型: {item['WeaponType']}")

        if item['Damage'] != -1:
            info.append(f"伤害: {item['Damage']}")

        if item['Crit'] != 0:
            info.append(f"击退: +{item['Crit']}%")

        if item['Shoot'] != 0:
            info.append(f"发射: {item['ShootName']} ({item['Shoot']})")

        if item['Mana'] != 0:
            info.append(f"消耗魔力: {item['Mana']}点")

        if item['Pick'] != 0:
            info.append(f"镐力: +{item['Pick']}%")

        if item['Axe'] != 0:
            info.append(f"斧力: +{item['Axe']}%")

        if item['Hammer'] != 0:
            info.append(f"锤力: +{item['Hammer']}%")

        if item['HealLife'] != 0:
            info.append(f"恢复生命: {item['HealLife']}点")

        if item['HealMana'] != 0:
            info.append(f"恢复魔力: {item['HealMana']}点")

        if item['BuffType'] != 0:
            info.append(f"增益: {item['BuffName']} ({item['BuffType']})")

        if item['CreateTile'] != -1:
            info.append(f"物块ID: {item['CreateTile']} ({item['PlaceStyle']})")

        if item['CreateWall'] != -1:
            info.append(f"墙ID: {item['CreateWall']}")

        monetary_value = item['MonetaryValue']

        if any(value != 0 for value in monetary_value.values()):
            monetary_info = (
                f"价值: {str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}")
            info.append(monetary_info)
        else:
            info.append("价值: 无价")

        if item['Description'] != "":
            info.append(f"{item['Description']}", )

        if item['Alias']:
            info.append("别名: " + ",".join(item['Alias']))

        byte_arr = io.BytesIO()
        image_key = f"item_{item['ItemId']}"

        if image_key in LookBag.image_cache:
            LookBag.image_cache[image_key].save(byte_arr, format='PNG', save_all=True)
            return MessageSegment.text("\n".join(info)) + MessageSegment.file_image(byte_arr)

        return MessageSegment.text("\n".join(info))

    @classmethod
    def _get_npc_info_string(cls, item):
        info = [f"生物名: {item['Name']}", f"ID: {item['NpcId']}", f"生命值: {item['LifeMax']}"]

        if item['Damage'] != -1:
            info.append(f"伤害: {item['Damage']}")

        monetary_value = item['MonetaryValue']

        if any(value != 0 for value in monetary_value.values()):
            monetary_info = (
                f"价值: {str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}")
            info.append(monetary_info)
        else:
            info.append("价值: 无价")

        if item['Description'] != "":
            info.append(f"{item['Description']}")

        if item['Alias']:
            info.append("别名: " + ",".join(item['Alias']))

        byte_arr = io.BytesIO()
        image_key = f"npc_{item['NpcId']}"

        if image_key in LookBag.image_cache:
            LookBag.image_cache[image_key].save(byte_arr, format='PNG', save_all=True)
            return MessageSegment.text("\n".join(info)) + MessageSegment.file_image(byte_arr)

        return MessageSegment.text("\n".join(info))

    @classmethod
    def _get_project_info_string(cls, item):
        info = [f"弹幕名: {item['Name']}", f"ID: {item['ProjId']}", f"AI类型: {item['AiStyle']}",
                f"友方: {item['Friendly']}"]

        if item['Alias']:
            info.append("别名: " + ",".join(item['Alias']))

        byte_arr = io.BytesIO()
        image_key = f"projectile_{item['ProjId']}"

        if image_key in LookBag.image_cache:
            LookBag.image_cache[image_key].save(byte_arr, format='PNG', save_all=True)
            return MessageSegment.text("\n".join(info)) + MessageSegment.file_image(byte_arr)

        return MessageSegment.text("\n".join(info))

    @classmethod
    def _get_buff_info_string(cls, item):
        info = [f"增益名: {item['Name']}", f"ID: {item['BuffId']}"]
        if item['Description'] != "":
            info.append(f"{item['Description']}")

        if item['Alias']:
            info.append("别名: " + ",".join(item['Alias']))
        byte_arr = io.BytesIO()
        LookBag.image_cache[f"buff_{item['BuffId']}"].save(byte_arr, format='PNG')
        return MessageSegment.text("\n".join(info)) + MessageSegment.file_image(byte_arr)

    @classmethod
    def _get_prefix_info_string(cls, item):
        info = [f"修饰语: {item['Name']}", f"ID: {item['PrefixId']}"]

        if item['Alias']:
            info.append("别名: " + ",".join(item['Alias']))

        return MessageSegment.text("\n".join(info))

    @classmethod
    def _get_config_info_string(cls, item):
        info = [f"键: {item['Name']}", f"配置文件: {item['Path']}", f"类型: {item['Type']}",
                f"默认值: {item['Default']}", f"描述: {item['Description']}"]

        return MessageSegment.text("\n".join(info))

    @classmethod
    def _get_permission_info_string(cls, item):
        info = [f"权限名: {item['Name']}"]

        if item['RelevantCommands']:
            info.append("相关命令: " + ",".join(item['RelevantCommands']))

        info.append(f"描述: {item['Description']}")

        return MessageSegment.text("\n".join(info))

    @classmethod
    def _enhanced_search(cls, query, dataset, id_field, name_field, alias_field='Alias'):
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

            if isinstance(aliases, str):
                aliases = [aliases]

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

    @classmethod
    def _get_search_result(cls, query, dataset, id_field, name_field, info_func, alias_field='Alias'):
        """通用搜索处理函数"""
        matched = cls._enhanced_search(query, dataset, id_field, name_field, alias_field)

        if not matched:
            return "啥东西都没找到哦!"
        elif len(matched) == 1:
            return info_func(matched[0])
        else:
            limit = min(80, len(matched))
            return f"找到{len(matched)}个匹配结果{f'(已展示{limit}个)' if limit != len(matched) else ''}: " + ", ".join(
                [f'{item[name_field]}({item[id_field]})' for item in matched[:limit]]
            )

    @classmethod
    def search_item(cls, query):
        return cls._get_search_result(query, cls.items, "ItemId", "Name", cls._get_item_info_string)

    @classmethod
    def search_npc(cls, query):
        return cls._get_search_result(query, cls.NPCs, "NpcId", "Name", cls._get_npc_info_string)

    @classmethod
    def search_projectile(cls, query):
        return cls._get_search_result(query, cls.projectiles, "ProjId", "Name", cls._get_project_info_string)

    @classmethod
    def search_buff(cls, query):
        return cls._get_search_result(query, cls.buffs, "BuffId", "Name", cls._get_buff_info_string)

    @classmethod
    def search_prefix(cls, query):
        return cls._get_search_result(query, cls.prefixes, "PrefixId", "Name", cls._get_prefix_info_string)

    @classmethod
    def search_config(cls, query):
        return cls._get_search_result(query, cls.configs, "ShortName", "Name", cls._get_config_info_string,
                                      "Description")

    @classmethod
    def search_permission(cls, query):
        return cls._get_search_result(query, cls.permissions, "ShortName", "Name", cls._get_permission_info_string,
                                      "Description")
