import json
from pathlib import Path

from fuzzywuzzy import fuzz
from nonebot.log import logger

from caibotlite.markdown.image import get_terraria_image

_ASSETS = Path("assets/images")


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
        with open(
            "assets/terraria_data/item_id.json", encoding="utf-8", errors="ignore"
        ) as fp:
            cls.items = json.loads(fp.read())

        with open(
            "assets/terraria_data/prefix_id.json", encoding="utf-8", errors="ignore"
        ) as fp:
            cls.prefixes = json.loads(fp.read())

        with open(
            "assets/terraria_data/project_id.json", encoding="utf-8", errors="ignore"
        ) as fp:
            cls.projectiles = json.loads(fp.read())

        with open(
            "assets/terraria_data/npc_id.json", encoding="utf-8", errors="ignore"
        ) as fp:
            cls.NPCs = json.loads(fp.read())

        with open(
            "assets/terraria_data/npcx_id.json", encoding="utf-8", errors="ignore"
        ) as fp:
            cls.NPCs.extend(json.loads(fp.read()))

        with open(
            "assets/terraria_data/buff_id.json", encoding="utf-8", errors="ignore"
        ) as fp:
            cls.buffs = json.loads(fp.read())

    logger.success("[terraria_search]物品、前缀、生物、buffs、弹幕已缓存!")

    @classmethod
    def _get_item_info_string(cls, item):
        item_id = item["ItemId"]
        lines = []

        # Inline image (only when the local file actually exists)
        if (_ASSETS / "items" / f"Item_{item_id}.png").is_file():
            lines.append(get_terraria_image("item", item_id))

        lines += [
            f"**{item['Name']}** (ID: **{item_id}**)",
            f"- 最大堆叠: **{item['MaxStack']}**",
        ]

        if item["WeaponType"]:
            lines.append(f"- 武器类型: **{item['WeaponType']}**")

        if item["Damage"] != -1:
            lines.append(f"- 伤害: **{item['Damage']}**")

        if item["Crit"] != 0:
            lines.append(f"- 击退: **+{item['Crit']}%**")

        if item["Shoot"] != 0:
            lines.append(f"- 发射: **{item['ShootName']}** (**{item['Shoot']}**)")

        if item["Mana"] != 0:
            lines.append(f"- 消耗魔力: **{item['Mana']}点**")

        if item["Pick"] != 0:
            lines.append(f"- 镐力: **+{item['Pick']}%**")

        if item["Axe"] != 0:
            lines.append(f"- 斧力: **+{item['Axe']}%**")

        if item["Hammer"] != 0:
            lines.append(f"- 锤力: **+{item['Hammer']}%**")

        if item["HealLife"] != 0:
            lines.append(f"- 恢复生命: **{item['HealLife']}点**")

        if item["HealMana"] != 0:
            lines.append(f"- 恢复魔力: **{item['HealMana']}点**")

        if item["BuffType"] != 0:
            lines.append(f"- 增益: **{item['BuffName']}** (**{item['BuffType']}**)")

        if item["CreateTile"] != -1:
            lines.append(
                f"- 物块ID: **{item['CreateTile']}** (**{item['PlaceStyle']}**)"
            )

        if item["CreateWall"] != -1:
            lines.append(f"- 墙ID: **{item['CreateWall']}**")

        monetary_value = item["MonetaryValue"]
        if any(value != 0 for value in monetary_value.values()):
            monetary_info = (
                f"- 价值: **{str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}**"
            )
            lines.append(monetary_info)
        else:
            lines.append("- 价值: **无价**")

        if item["Alias"]:
            lines.append("- 别名: **" + ",".join(item["Alias"]) + "**")

        if item["Description"] != "":
            lines.extend(f"> {line}" for line in item["Description"].splitlines())

        return "\n".join(lines)

    @classmethod
    def _get_npc_info_string(cls, item):
        npc_id = item["NpcId"]
        lines = []

        if (_ASSETS / "npcs" / f"NPC_{npc_id}.png").is_file():
            lines.append(get_terraria_image("npc", npc_id))

        lines += [
            f"**{item['Name']}** (ID: **{npc_id}**)",
            f"- 生命值: **{item['LifeMax']}**",
        ]

        if item["Damage"] != -1:
            lines.append(f"- 伤害: **{item['Damage']}**")

        monetary_value = item["MonetaryValue"]
        if any(value != 0 for value in monetary_value.values()):
            monetary_info = (
                f"- 价值: **{str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}**"
            )
            lines.append(monetary_info)
        else:
            lines.append("- 价值: **无价**")

        if item["Alias"]:
            lines.append("- 别名: **" + ",".join(item["Alias"]) + "**")

        if item["Description"] != "":
            lines.extend(f"> {line}" for line in item["Description"].splitlines())

        return "\n".join(lines)

    @classmethod
    def _get_project_info_string(cls, item):
        proj_id = item["ProjId"]
        lines = []

        if (_ASSETS / "projectiles" / f"Projectile_{proj_id}.png").is_file():
            lines.append(get_terraria_image("projectile", proj_id))

        lines += [
            f"**{item['Name']}** (ID: **{proj_id}**)",
            f"- AI类型: **{item['AiStyle']}**",
            f"- 友方: **{item['Friendly']}**",
        ]

        if item["Alias"]:
            lines.append("- 别名: " + ",".join(item["Alias"]))

        return "\n".join(lines)

    @classmethod
    def _get_buff_info_string(cls, item):
        buff_id = item["BuffId"]
        lines = []

        if (_ASSETS / "buffs" / f"Buff_{buff_id}.png").is_file():
            lines.append(get_terraria_image("buff", buff_id))

        lines += [f"**{item['Name']}** (ID: **{buff_id}**)"]

        if item["Alias"]:
            lines.append("- 别名: **" + ",".join(item["Alias"]) + "**")

        if item["Description"] != "":
            lines.extend(f"> {line}" for line in item["Description"].splitlines())

        return "\n".join(lines)

    @classmethod
    def _get_prefix_info_string(cls, item):
        lines = [f"**{item['Name']}** (ID: **{item['PrefixId']}**)"]

        if item["Alias"]:
            lines.append("- 别名: **" + ",".join(item["Alias"]) + "**")

        return "\n".join(lines)

    @classmethod
    def _enhanced_search(
        cls, query, dataset, id_field, name_field, alias_field="Alias"
    ):
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
    def _get_search_result(
        cls, query, dataset, id_field, name_field, info_func, alias_field="Alias"
    ):
        """通用搜索处理函数"""
        matched = cls._enhanced_search(
            query, dataset, id_field, name_field, alias_field
        )

        if not matched:
            return "啥东西都没找到哦!"
        elif len(matched) == 1:
            return info_func(matched[0])
        else:
            limit = min(80, len(matched))
            return (
                f"找到{len(matched)}个匹配结果{f'(已展示{limit}个)' if limit != len(matched) else ''}: "
                + ", ".join(
                    [
                        f"{item[name_field]}({item[id_field]})"
                        for item in matched[:limit]
                    ]
                )
            )

    @classmethod
    def search_item(cls, query):
        return cls._get_search_result(
            query, cls.items, "ItemId", "Name", cls._get_item_info_string
        )

    @classmethod
    def search_npc(cls, query):
        return cls._get_search_result(
            query, cls.NPCs, "NpcId", "Name", cls._get_npc_info_string
        )

    @classmethod
    def search_projectile(cls, query):
        return cls._get_search_result(
            query, cls.projectiles, "ProjId", "Name", cls._get_project_info_string
        )

    @classmethod
    def search_buff(cls, query):
        return cls._get_search_result(
            query, cls.buffs, "BuffId", "Name", cls._get_buff_info_string
        )

    @classmethod
    def search_prefix(cls, query):
        return cls._get_search_result(
            query, cls.prefixes, "PrefixId", "Name", cls._get_prefix_info_string
        )
