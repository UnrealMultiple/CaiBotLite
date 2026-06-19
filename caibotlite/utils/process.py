from caibotlite.constants import API_URL
from urllib.parse import quote

from caibotlite.markdown.image import get_image

PROCESS_ICON_MAP = {
    "已毕业": "Black_Graduation_Cap.webp",
    "月总前": "Map_Icon_Moon_Lord.webp",
    "月亮领主前": "Map_Icon_Moon_Lord.webp",
    "四柱前": "Bestiary_Nebula_Pillar",
    "天界柱前": "Bestiary_Nebula_Pillar",
    "拜月教徒前": "Map_Icon_Lunatic_Cultist.webp",
    "拜月教邪教徒前": "Map_Icon_Lunatic_Cultist.webp",
    "石巨人前": "Map_Icon_Golem.webp",
    "世花前": "Map_Icon_Plantera_(first_form).webp",
    "世纪之花前": "Map_Icon_Plantera_(first_form).webp",
    "美杜莎前": "Ocram's_Razor.webp",
    "新三王前": "Map_Icon_Skeletron_Prime.webp",
    "血肉墙前": "Map_Icon_Wall_of_Flesh.webp",
    "骷髅王前": "Map_Icon_Skeletron.webp",
    "世吞/克脑前": "Map_Icon_Eater_of_Worlds.webp",
    "克脑前": "Map_Icon_Brain_of_Cthulhu.webp",
    "克苏鲁之脑前": "Map_Icon_Brain_of_Cthulhu.webp",
    "世吞前": "Map_Icon_Eater_of_Worlds.webp",
    "世界吞噬怪前": "Map_Icon_Eater_of_Worlds.webp",
    "克眼前": "Map_Icon_Eye_of_Cthulhu_(first_form).webp",
    "克苏鲁之眼前": "Map_Icon_Eye_of_Cthulhu_(first_form).webp",
    "史王前": "Map_Icon_King_Slime.webp",
    "史莱姆王前": "Map_Icon_King_Slime.webp",
}


def get_process_icon(process: str) -> str:
    icon_name = PROCESS_ICON_MAP.get(process.strip(), "")
    if not icon_name:
        return ""

    return get_image(f"{API_URL.rstrip('/')}/image/{quote(icon_name)}")

