import os
import time
from typing import Dict

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling
from nonebot.log import logger

from caibotlite.utils.text import filter_all

Vault = Image.open("assets/images/items/Item_4076.png").convert('RGBA')
Vault = Vault.resize((70, 70), Resampling.LANCZOS)
_, _, _, aVault = Vault.split()

minecart = Image.open("assets/images/items/Item_2343.png").convert('RGBA')
minecart = minecart.resize((65, 65), Resampling.LANCZOS)
_, _, _, a_minecart = minecart.split()

safe = Image.open("assets/images/items/Item_346.png").convert('RGBA')
safe = safe.resize((70, 70), Resampling.LANCZOS)
_, _, _, a_safe = safe.split()

Satchel = Image.open("assets/images/items/Item_5343.png").convert('RGBA')
Satchel = Satchel.resize((70, 70), Resampling.LANCZOS)
_, _, _, aSatchel = Satchel.split()

Forge = Image.open("assets/images/items/Item_3813.png").convert('RGBA')
Forge = Forge.resize((70, 70), Resampling.LANCZOS)
_, _, _, aForge = Forge.split()

WoodenArrow = Image.open("assets/images/items/Item_40.png").convert('RGBA')
WoodenArrow = WoodenArrow.resize((70, 70), Resampling.LANCZOS)
_, _, _, aWoodenArrow = WoodenArrow.split()

pig = Image.open("assets/images/items/Item_87.png").convert('RGBA')
pig = pig.resize((80, 80), Resampling.LANCZOS)
_, _, _, apig = pig.split()

Red_Drug = Image.open("assets/images/items/Item_678.png").convert('RGBA')
Red_Drug = Red_Drug.resize((70, 70), Resampling.LANCZOS)
_, _, _, aRed_Drug = Red_Drug.split()

Arkhalis = Image.open("assets/images/items/Item_3368.png").convert('RGBA')
Arkhalis = Arkhalis.resize((70, 70), Resampling.LANCZOS)
_, _, _, aArkhalis = Arkhalis.split()

book = Image.open("assets/images/items/Item_149.png").convert('RGBA')
book = book.resize((70, 70), Resampling.LANCZOS)
_, _, _, abook = book.split()

advanced_combat_techniques_two = Image.open("assets/images/items/Item_5336.png").convert('RGBA')
advanced_combat_techniques_two = advanced_combat_techniques_two.resize((70, 70), Resampling.LANCZOS)
_, _, _, aadvanced_combat_techniques_two = advanced_combat_techniques_two.split()

defender_medal = Image.open("assets/images/items/Item_3817.png").convert('RGBA')
defender_medal = defender_medal.resize((50, 50), Resampling.LANCZOS)
_, _, _, adefender_medal = defender_medal.split()

warrior_emblem = Image.open("assets/images/items/Item_490.png").convert('RGBA')
warrior_emblem = warrior_emblem.resize((50, 50), Resampling.LANCZOS)
_, _, _, awarrior_emblem = warrior_emblem.split()

the_plan = Image.open("assets/images/items/Item_903.png").convert('RGBA')
the_plan = the_plan.resize((50, 50), Resampling.LANCZOS)
_, _, _, athe_plan = the_plan.split()

life_item = Image.open("assets/images/items/Item_58.png").convert('RGBA')
life_item = life_item.resize((70, 70), Resampling.LANCZOS)
_, _, _, alife_item = life_item.split()

mana_item = Image.open("assets/images/items/Item_184.png").convert('RGBA')
mana_item = mana_item.resize((70, 70), Resampling.LANCZOS)
_, _, _, amana_item = mana_item.split()

sitting_duck_fishing_pole = Image.open("assets/images/items/Item_2296.png").convert('RGBA')
sitting_duck_fishing_pole = sitting_duck_fishing_pole.resize((50, 50), Resampling.LANCZOS)
_, _, _, asitting_duck_fishing_pole = sitting_duck_fishing_pole.split()

golden_fishing_rod = Image.open("assets/images/items/Item_2294.png").convert('RGBA')
golden_fishing_rod = golden_fishing_rod.resize((50, 50), Resampling.LANCZOS)
_, _, _, agolden_fishing_rod = golden_fishing_rod.split()

advanced_combat_techniques = Image.open("assets/images/items/Item_4382.png").convert('RGBA')
advanced_combat_techniques = advanced_combat_techniques.resize((50, 50), Resampling.LANCZOS)
_, _, _, aadvanced_combat_techniques = advanced_combat_techniques.split()

Trash = Image.open("assets/images/items/Trash.png").convert('RGBA')
_, _, _, aTrash = Trash.split()

One = Image.open("assets/images/items/Item_2703.png").convert('RGBA')
One = One.resize((70, 70), Resampling.LANCZOS)
_, _, _, aOne = One.split()

Two = Image.open("assets/images/items/Item_2704.png").convert('RGBA')
Two = Two.resize((70, 70), Resampling.LANCZOS)
_, _, _, aTwo = Two.split()

Three = Image.open("assets/images/items/Item_2705.png").convert('RGBA')
Three = Three.resize((70, 70), Resampling.LANCZOS)
_, _, _, aThree = Three.split()

back3 = Image.open("assets/images/items/Inventory_Back7.png").convert('RGBA')
back4 = Image.open("assets/images/items/Inventory_Back8.png").convert('RGBA')
back5 = Image.open("assets/images/items/Inventory_Back3.png").convert('RGBA')
back1 = Image.open("assets/images/items/Inventory_Back.png").convert('RGBA')
back6 = Image.open("assets/images/items/Inventory_Back12.png").convert('RGBA')
back2 = Image.open("assets/images/items/Inventory_Back11.png").convert('RGBA')
_, _, _, a = back1.split()
_, _, _, a2 = back2.split()
font = "assets/fonts/LXGWWenKaiMono-Medium.ttf"


# noinspection LongLine
class LookBag:
    image_cache = {}

    @classmethod
    def init_look_bag(cls):
        item_dir = "assets/images/items/"
        buff_dir = "assets/images/buffs/"

        for filename in os.listdir(item_dir):
            if filename.endswith(".png") and filename.startswith("Item"):
                item_id = filename.split("_")[1].split(".")[0]
                cls.image_cache[f"item_{item_id}"] = Image.open(os.path.join(item_dir, filename)).convert("RGBA")

        for filename in os.listdir(buff_dir):
            if filename.endswith(".png") and filename.startswith("Buff"):
                buff_id = filename.split("_")[1].split(".")[0]
                cls.image_cache[f"buff_{buff_id}"] = Image.open(os.path.join(buff_dir, filename)).convert("RGBA")

        logger.success("[look_bag]图片缓存完成!")

    @classmethod
    def draw_item(cls, bg_img: Image, draw: ImageDraw, x: int, y: int, item_id: int, stack: int):
        try:

            item = cls.image_cache.get(f"item_{item_id}")
            if item is None:
                raise ValueError(f"Image with ID {item_id} not found in cache.")

            item_font = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=14)

            r, g, b, a = item.split()
            bg_img.paste(item, (x, y), mask=a)
            if stack != 1 and stack != 0:
                draw.text((x + 6, y + 30), str(stack), font=item_font)
        except Exception as e:
            logger.error(f"查背包图片绘制出错: {e}")
            pass

    @classmethod
    def draw_buff(cls, bg_img: Image, draw: ImageDraw, x: int, y: int, buff_id: int):
        try:
            if buff_id == 0:
                return

            buff = cls.image_cache.get(f"buff_{buff_id}")
            if buff is None:
                raise ValueError(f"buffs image with ID {buff_id} not found in cache.")

            _, _, _, a2 = buff.split()
            bg_img.paste(buff, (x, y), mask=a2)
        except Exception as e:
            logger.error(f"查背包图片绘制出错: {e}")
            pass

    @classmethod
    def get_bag_png(cls, payload: Dict) -> Image:
        name = filter_all(payload['name'])
        inv = payload['inventory']
        buffs = payload['buffs']
        enhances = payload['enhances']
        life = payload['life']
        mana = payload['mana']
        quests_completed = payload['quests_completed']
        economic = payload['economic']

        bg_img = Image.open("assets/images/backgrounds/Background_4.png").convert('RGBA')
        ft = ImageFont.truetype(font=font, size=100)
        w, h = bg_img.size
        draw = ImageDraw.Draw(bg_img)
        _, _, text_w, text_h = draw.textbbox((0, 0), "name", font=ft)
        draw.text(((w - text_w) / 2, 0), name, font=ft)
        draw = ImageDraw.Draw(bg_img)
        ft = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=30)
        draw.text((10, 1040), "By Cai", font=ft)
        draw.text((160, 1040), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), font=ft)

        for h in range(5):
            for i in range(10):
                bg_img.paste(back1, (150 + i * back1.width, back1.height * h + 120), mask=a)  # 背包
        index = 0
        for h in range(5):
            for i in range(10):
                cls.draw_item(bg_img, draw, 150 + i * back1.width, back1.height * h + 120, inv[index][0], inv[index][1])
                index += 1

        bg_img.paste(Satchel, (150 - 60, Satchel.height * 1 + 40), mask=aSatchel)

        for h in range(4):
            for i in range(10):
                bg_img.paste(back2, (740 + i * back2.width, back2.height * h + 120), mask=a2)  # 猪猪
        index = 99

        for h in range(4):
            for i in range(10):
                cls.draw_item(bg_img, draw, 740 + i * back2.width, back2.height * h + 120, inv[index][0], inv[index][1])
                index += 1

        bg_img.paste(pig, (740 - 65, back2.height * 2), mask=apig)
        for h in range(4):
            for i in range(10):
                bg_img.paste(back2, (1330 + i * back2.width, back2.height * h + 120), mask=a)  # 保险
        for h in range(4):
            for i in range(10):
                cls.draw_item(bg_img, draw, 1330 + i * back2.width, back2.height * h + 120, inv[index][0],
                              inv[index][1])
                index += 1

        bg_img.paste(safe, (1330 - 60, back2.height * 2 + 5), mask=a_safe)

        index += 1

        for h in range(4):
            for i in range(10):
                bg_img.paste(back2, (1330 + i * back2.width, back2.height * h + 120 + 280), mask=a)  # 熔炉
        for h in range(4):
            for i in range(10):
                cls.draw_item(bg_img, draw, 1330 + i * back2.width, back2.height * h + 120 + 280, inv[index][0],
                              inv[index][1])
                index += 1

        bg_img.paste(Forge, (1330 - 60, back2.height * 2 + 25 + 265), mask=aForge)

        for h in range(4):
            for i in range(10):
                bg_img.paste(back2, (1330 + i * back2.width, back2.height * h + 120 + 280 + 280), mask=a)
        for h in range(4):
            for i in range(10):
                cls.draw_item(bg_img, draw, 1330 + i * back2.width, back2.height * h + 120 + 280 + 280, inv[index][0],
                              inv[index][1])  # 虚空袋
                index += 1

        bg_img.paste(Vault, (1330 - 55, back2.height * 2 + 25 + 280 + 265), mask=aVault)

        for h in range(10):
            bg_img.paste(back3, (150, back2.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back4, (150 + back3.width, back2.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back5, (150 + back3.width + back4.width, back2.height * h + 120 + 280 + 30), mask=a)
        index = 59

        for h in range(10):
            cls.draw_item(bg_img, draw, 150 + back3.width + back4.width, back2.height * h + 120 + 280 + 30,
                          inv[index][0],
                          inv[index][1])  # 盔甲饰品
            index += 1
        for h in range(10):
            cls.draw_item(bg_img, draw, 150 + back3.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                          inv[index][1])  # 盔甲饰品
            index += 1
        for h in range(10):
            cls.draw_item(bg_img, draw, 150, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])
            # 染料
            index += 1

        bg_img.paste(One, (155 - 60, 120 + 280 + 20), mask=aOne)
        index = 290

        for h in range(10):
            bg_img.paste(back3, (350, back2.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back4, (350 + back3.width, back2.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back5, (350 + back3.width + back4.width, back2.height * h + 120 + 280 + 30), mask=a)
        for h in range(10):
            cls.draw_item(bg_img, draw, 350 + back3.width + back4.width, back2.height * h + 120 + 280 + 30,
                          inv[index][0],
                          inv[index][1])  # 盔甲饰品
            index += 1
        for h in range(10):
            cls.draw_item(bg_img, draw, 350 + back3.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                          inv[index][1])  # 盔甲饰品
            index += 1
        for h in range(10):
            cls.draw_item(bg_img, draw, 350, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])
            # 染料
            index += 1

        bg_img.paste(Two, (355 - 60, 120 + 280 + 20), mask=aTwo)
        for h in range(10):
            bg_img.paste(back3, (550, back3.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back4, (550 + back3.width, back2.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back5, (550 + back3.width + back4.width, back2.height * h + 120 + 280 + 30), mask=a)
        for h in range(10):
            cls.draw_item(bg_img, draw, 550 + back3.width + back4.width, back2.height * h + 120 + 280 + 30,
                          inv[index][0],
                          inv[index][1])  # 盔甲饰品
            index += 1
        for h in range(10):
            cls.draw_item(bg_img, draw, 550 + back3.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                          inv[index][1])  # 盔甲饰品
            index += 1
        for h in range(10):
            cls.draw_item(bg_img, draw, 550, back3.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])
            # 染料
            index += 1

        bg_img.paste(Three, (555 - 60, 120 + 280 + 20), mask=aThree)
        for h in range(5):
            bg_img.paste(back1, (750, back2.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back1, (750 + back2.width, back2.height * h + 120 + 280 + 30), mask=a)
        index = 89
        for h in range(5):
            cls.draw_item(bg_img, draw, 750 + back2.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                          inv[index][1])  # 坐骑宠物
            index += 1
        for h in range(5):
            cls.draw_item(bg_img, draw, 750, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 染料
            index += 1

        bg_img.paste(minecart, (755 - 60, 125 + 280 + 15), mask=a_minecart)

        for h in range(4):
            bg_img.paste(back1, (900, back2.height * h + 120 + 280 + 30), mask=a)
            bg_img.paste(back1, (900 + back2.width, back2.height * h + 120 + 280 + 30), mask=a)
        index = 50
        for h in range(4):
            cls.draw_item(bg_img, draw, 900, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 坐骑宠物
            index += 1
        for h in range(4):
            cls.draw_item(bg_img, draw, 900 + back2.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                          inv[index][1])  # 染料
            index += 1

        bg_img.paste(WoodenArrow, (915 - 65, 120 + 280 + 20), mask=aWoodenArrow)
        bg_img.paste(back6, (900 + back2.width, back2.height * 4 + 120 + 280 + 30), mask=a)
        bg_img.paste(back6, (900, back2.height * 4 + 120 + 280 + 30), mask=a)
        bg_img.paste(Trash, (900 + 10, back2.height * 4 + 120 + 280 + 30 + 10), mask=aTrash)
        cls.draw_item(bg_img, draw, 900 + back2.width, back2.height * 4 + 120 + 280 + 30, inv[179][0], inv[179][1])

        buffs = [i for i in buffs if i != 0]
        if len(buffs) != 0:
            index = 0

            bg_img.paste(Red_Drug, (712 - 15, 120 + 600 + 8), mask=aRed_Drug)
            for h in range(6):
                for b in range(8):
                    if index >= len(buffs):
                        break
                    cls.draw_buff(bg_img, draw, 750 + 34 * b, + 120 + 600 + 30 + 34 * h, buffs[index])
                    index += 1

        bg_img.paste(book, (915 + 50 + 50, 120 + 280 + 20), mask=abook)
        font1 = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=38)
        draw.text((915 + 50 + 60 + 50, 120 + 280 + 30), "玩家信息", font=font1, fill=(0, 0, 0))
        font2 = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=30)

        bg_img.paste(life_item, (915 + 50 + 60, 120 + 280 + 30 + 30 + 15), mask=alife_item)
        draw.text((915 + 50 + 60 + 50, 120 + 280 + 30 + 30 + 30), "生命:" + life, font=font2, fill=(255, 106, 106))

        bg_img.paste(mana_item, (915 + 50 + 60, 120 + 280 + 30 + 30 + 15 + 40), mask=amana_item)
        draw.text((915 + 50 + 60 + 50, 120 + 280 + 30 + 30 + 30 + 40), "魔力:" + mana, font=font2, fill=(30, 144, 255))

        if quests_completed >= 50:
            bg_img.paste(golden_fishing_rod, (915 + 50 + 70, 120 + 280 + 30 + 30 + 30 + 40 + 40),
                         mask=agolden_fishing_rod)
            draw.text((915 + 50 + 60 + 50, 120 + 280 + 30 + 30 + 30 + 40 + 40), f"渔夫任务数:{quests_completed}次",
                      font=font2, fill=(255, 223, 0))
        else:
            bg_img.paste(sitting_duck_fishing_pole, (915 + 50 + 70, 120 + 280 + 30 + 30 + 30 + 40 + 30),
                         mask=asitting_duck_fishing_pole)
            draw.text((915 + 50 + 60 + 50, 120 + 280 + 30 + 30 + 30 + 40 + 40), f"渔夫任务数:{quests_completed}次",
                      font=font2, fill=(0, 0, 205))

        bg_img.paste(advanced_combat_techniques, (915 + 50 + 70, 120 + 280 + 30 + 30 + 30 + 40 + 40 + 30),
                     mask=aadvanced_combat_techniques)
        if len(enhances) == 0:
            draw.text((915 + 50 + 60 + 50, 120 + 280 + 30 + 30 + 30 + 40 + 40 + 40), f"永久增益:无", font=font2,
                      fill=(112, 128, 144))
        else:
            draw.text((915 + 50 + 60 + 50, 120 + 280 + 30 + 30 + 30 + 40 + 40 + 40), f"永久增益:", font=font2,
                      fill=(255, 20, 147))

        if len(enhances) != 0:
            index = 0
            for b in range(len(enhances)):
                cls.draw_item(bg_img, draw, 915 + 50 + 60 + 50 + 130 + 35 * b,
                              120 + 280 + 30 + 30 + 30 + 40 + 40 + 30 + 5,
                              enhances[index],
                              1)
                index += 1

        if len(economic) != 0 and economic['Coins'] != "":
            bg_img.paste(advanced_combat_techniques_two, (915 + 50 + 50, 250 + 120 + 280 + 20),
                         mask=aadvanced_combat_techniques_two)
            draw.text((915 + 50 + 60 + 50, 250 + 120 + 280 + 30), "Economic", font=font1, fill=(138, 43, 226))

            bg_img.paste(defender_medal, (915 + 50 + 70, 250 + 120 + 280 + 30 + 30 + 22), mask=adefender_medal)
            draw.text((915 + 50 + 60 + 50, 120 + 250 + 280 + 30 + 30 + 30), economic['Coins'], font=font2,
                      fill=(255, 215, 0))
            economic['Coins']: str
            h = economic['Coins'].count("\n") + 1
            if economic['LevelName'] != "":
                bg_img.paste(warrior_emblem, (915 + 50 + 70, 250 + 120 + 280 + 30 + 30 + 22 + 40 * h),
                             mask=awarrior_emblem)
                draw.text((915 + 50 + 60 + 50, 250 + 120 + 280 + 30 + 30 + 30 + 40 * h), economic['LevelName'],
                          font=font2,
                          fill=(30, 144, 255))
                h += 1

            if economic['Skill'] != "":
                bg_img.paste(the_plan, (915 + 50 + 70, 250 + 120 + 280 + 30 + 30 + 22 + 40 * h),
                             mask=the_plan)
                draw.text((915 + 50 + 60 + 50, 250 + 120 + 280 + 30 + 30 + 30 + 40 * h), economic['Skill'],
                          font=font2, fill=(0, 0, 205))

        return bg_img


if __name__ == '__main__':
    data = {"type": "lookbag", "name": "Cai", "exist": 1, "life": "9999/9999", "mana": "20/20", "quests_completed": 0,
            "inventory": [[3509, 1], [5011, 1], [3506, 1], [8, 5], [183, 7], [3509, 1], [706, 10], [4444, 1],
                          [2589, 10], [4808, 1], [3509, 1], [3509, 1], [3509, 1], [3509, 1], [3509, 1], [3509, 1],
                          [3509, 1], [4808, 1], [4956, 1], [3330, 4], [3509, 1], [3509, 1], [3509, 1], [3509, 1],
                          [3509, 1], [3509, 1], [4808, 1], [499, 1484], [188, 51], [361, 9999], [3509, 1], [3509, 1],
                          [965, 35], [307, 7], [4934, 1], [27, 2], [28, 2], [5, 7], [1425, 9999], [602, 9994],
                          [3509, 1], [3509, 1], [75, 84], [38, 15], [3509, 1], [2544, 1], [9, 31], [593, 1742],
                          [313, 10], [43, 9998], [2, 3], [72, 75], [71, 5], [73, 1], [40, 183], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [4779, 1], [4780, 1], [4781, 1], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [150, 1], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3],
                          [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [1, 0]], "buffs": [1, 2, 1, 2],
            "enhances": [1, 2, 3, 2],
            "economic": {
                "Coins": "原石:3000",  # 纯属乱写，切勿当真
                "Skill": "技能:玩原神",
                "LevelName": "职业:原批",

            }, "group_id": 991556763}
    # data['economic']['Coins'] = data['economic']['Coins']
    # data['economic']['LevelName'] = data['economic']['LevelName']
    # data['economic']['Skill'] = data['economic']['Skill']
    img = LookBag.get_bag_png(data['name'], data['inventory'], data['buffs'], data['enhances'], data['life'],
                              data['mana'], data['quests_completed'], data['economic'])
    img.show()
