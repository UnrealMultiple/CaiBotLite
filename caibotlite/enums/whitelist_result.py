from enum import Enum


class WhitelistResult(str, Enum):
    ACCEPT = "accept"
    NEED_LOGIN = "need_login"
    NOT_IN_WHITELIST = "not_in_whitelist"
    In_GROUP_BLACKLIST = "in_group_blacklist"
    In_BOT_BLACKLIST = "in_bot_blacklist"
