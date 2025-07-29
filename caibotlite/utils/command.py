from functools import cache
from typing import List

import nonebot
from fuzzywuzzy import fuzz


@cache
def get_registered_commands() -> List[str]:
    commands = []
    for p in nonebot.get_loaded_plugins():
        for m in p.matcher:
            for checker in m.rule.checkers:
                callable_obj = checker.call
                if hasattr(callable_obj, 'cmds'):
                    for cmd_group in callable_obj.cmds:
                        commands.append(cmd_group[0])

    return commands


def match_like_command(query: str):
    results = []
    query_lower = query.lower()

    for command_name in get_registered_commands():
        name_lower = command_name.lower()
        best_score = 0
        # 2. 开头匹配（次高优先级）
        if command_name.startswith(query):
            best_score = max(best_score, 100)

        # 3. 包含匹配
        if query in command_name:
            best_score = max(best_score, 90)

        # 6. 模糊匹配
        ratio = fuzz.ratio(query_lower, name_lower)
        if ratio > 90:  # 降低阈值以增加召回率
            best_score = max(best_score, ratio)

        if best_score > 0:
            results.append((command_name, best_score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in results]
