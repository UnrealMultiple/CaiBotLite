import tomllib
from datetime import timedelta


def get_version():
    with open("./pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


BOT_VERSION = get_version()
BOT_APPID = 102256264
SUPERADMINS_OPEN_ID = ['EE21E1DA3297AB70A9A072816DD75E98', '0D8312FD9AAC272E1452C32706E859AA']
MAX_LOGIN_TIME = timedelta(minutes=5)


class WhiteList:
    MAX_NAME_LENGTH = 15


class FileSystem:
    MAX_FILE_SIZE_MB = 30
    FILE_EXPIRATION = timedelta(minutes=10).seconds
    FILE_DOWNLOAD_URL = "https://raw.terraria.ink"
