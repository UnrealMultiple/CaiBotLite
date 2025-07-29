import time

from PIL import Image, ImageDraw, ImageFont

ft_25 = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=25)
ft_30 = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=30)
ft_40 = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=40)
ft_60 = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=60)
ft_100 = ImageFont.truetype(font="assets/fonts/LXGWWenKaiMono-Medium.ttf", size=100)


class QueryProcess:
    @classmethod
    def transparent_back(cls, img):
        img = img.convert('RGBA')
        length, height = img.size

        for i in range(10):
            for h in range(height):
                color_0 = img.getpixel((i, h))
                for l in range(length):
                    dot = (l, h)
                    color_1 = img.getpixel(dot)
                    if color_1 == color_0:
                        color_1 = color_1[:-1] + (0,)
                        img.putpixel(dot, color_1)
        return img

    @classmethod
    def get_process_png(cls, process_data) -> Image:
        process = process_data["process"]
        kill_counts = process_data["kill_counts"]
        if process_data["zenith_world"]:
            img = Image.open("assets/images/backgrounds/Background_2.png")
        elif process_data["drunk_world"]:
            img = Image.open("assets/images/backgrounds/Background_3.png")
        else:
            img = Image.open("assets/images/backgrounds/Background_1.png")

        draw = ImageDraw.Draw(img)

        def draw_event(name, show_name, x, y):
            event_img = Image.open(f"assets/images/bosses/{name}.png")
            if event_img.mode != 'RGBA':
                event_img = event_img.convert('RGBA')
                event_img.save(f"assets/images/bosses/{name}.png")
            _, _, _, ba = event_img.split()
            img.paste(event_img, (x, y), mask=ba)
            _, _, tw, th = draw.textbbox((0, 0), show_name + ":", font=ft_25)
            draw.text((x + event_img.size[0], y), show_name + ":", font=ft_25)
            if name == "Old Ones Army":
                if process['DD2InvasionT3']:
                    draw.text((x + event_img.size[0] + tw, y), "T3", font=ft_25,
                              fill='blue')
                elif process['DD2InvasionT2']:
                    draw.text((x + event_img.size[0] + tw, y), "T2", font=ft_25,
                              fill='orange')
                elif process['DD2InvasionT1']:
                    draw.text((x + event_img.size[0] + tw, y), "T1", font=ft_25,
                              fill='red')
                else:
                    draw.text((x + event_img.size[0] + tw, y), "未击败", font=ft_25,
                              fill='black')
                return
            if name == "Pillars":
                if process[name]:
                    draw.text((x + event_img.size[0] + tw, y), "已击败", font=ft_25, fill='red')
                else:
                    not_defeat = []
                    if not process['Tower Stardust']:
                        not_defeat.append("星尘")
                    if not process['Tower Vortex']:
                        not_defeat.append("星璇")
                    if not process['Tower Nebula']:
                        not_defeat.append("星云")
                    if not process['Tower Solar']:
                        not_defeat.append("日耀")
                    draw.text((x + event_img.size[0] + tw, y), f"未击败({','.join(not_defeat)})", font=ft_25,
                              fill='black')
            if process[name]:
                draw.text((x + event_img.size[0] + tw, y), "已击败", font=ft_25, fill='red')
            else:
                draw.text((x + event_img.size[0] + tw, y), "未击败", font=ft_25,
                          fill='black')

        def draw_boss(name, x, y, up=0):
            boss_img = Image.open(f"assets/images/bosses/{name}.png")
            if boss_img.mode != 'RGBA':
                boss_img = boss_img.convert('RGBA')
                boss_img.save(f"assets/images/bosses/{name}.png")
            _, _, _, ba = boss_img.split()
            img.paste(boss_img, (x, y - up), mask=ba)
            _, _, tw, th = draw.textbbox((0, 0), "已击败", font=ft_40)
            if name == "Mechdusa":
                if process['The Destroyer'] and process['The Twins'] and process['Skeletron Prime']:
                    _, _, tw, th = draw.textbbox((0, 0), "已击败", font=ft_40)
                    draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), "已击败", font=ft_40,
                              fill='red')
                else:
                    not_defeat = []
                    if not process['The Destroyer']:
                        not_defeat.append("毁")
                    if not process['Skeletron Prime']:
                        not_defeat.append("骷")
                    if not process['The Twins']:
                        not_defeat.append("眼")

                    _, _, tw, th = draw.textbbox((0, 0), f"未击败({','.join(not_defeat)})", font=ft_40)
                    draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10),
                              f"未击败({','.join(not_defeat)})", font=ft_40)

                return
            if process[name]:
                _, _, tw, th = draw.textbbox((0, 0), f"已击败({kill_counts[name]}次)", font=ft_40)
                draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10),
                          f"已击败({kill_counts[name]}次)", font=ft_40, fill='red')
            else:
                _, _, tw, th = draw.textbbox((0, 0), "未击败", font=ft_40)
                if process_data['zenith_world']:
                    draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), "未击败", font=ft_40)
                else:
                    draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), "未击败", font=ft_40,
                              fill='black')

        max_w, max_h = img.size

        if len(process_data["world_name"]) > 7:
            _, _, w, h = draw.textbbox((0, 15), process_data["world_name"], font=ft_60)
            draw.text(((max_w - w) / 2, 15), process_data["world_name"], font=ft_60)

        else:
            _, _, w, h = draw.textbbox((0, 0), process_data["world_name"], font=ft_100)
            draw.text(((max_w - w) / 2, 0), process_data["world_name"], font=ft_100)

        icon = cls.transparent_back(Image.open(f"assets/images/world_icon/{process_data['world_icon']}.png"))
        icon = icon.resize((int(160 * 0.65), int(158 * 0.65)))
        _, _, _, a = icon.split()
        img.paste(icon, (int((max_w - w) / 2 - 160 * 0.65), 0), mask=a)

        _, _, w, h = draw.textbbox((0, 0), "进度", font=ft_60)
        draw.text(((max_w - w) / 2, 120), "进度", font=ft_60)

        draw.text((10, 1040), "By Cai", font=ft_30)  # 署名
        draw.text((150, 1040), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), font=ft_30)  # 时间

        draw_event("Goblins", "哥布林军队", 200, 50)
        draw_event("Pirates", "海盗入侵", 200 + 2, 50 + 24 * 1)
        draw_event("Frost", "雪人军团", 200 + 6, 50 + 24 * 2)
        draw_event("Frost Moon", "霜月", 200 + 4, 50 + 24 * 3)
        draw_event("Pumpkin Moon", "南瓜月", 200 + 4, 50 + 24 * 4)
        draw_event("Pillars", "四柱", 200 + 2, 50 + 24 * 5)
        draw_event("Old Ones Army", "旧日军团", 200, 50 + 24 * 6)

        draw_boss("King Slime", 180 + 280 * 0, 250)
        draw_boss("Eye of Cthulhu", 180 + 280 * 1 + 20, 250 - 10)
        draw_boss("Eater of Worlds", 180 + 280 * 2, 250 + 133, 50)
        draw_boss("Brain of Cthulhu", 180 + 280 * 3, 250 - 3)
        draw_boss("Queen Bee", 180 + 280 * 4, 250 + 18)
        draw_boss("Deerclops", 180 + 280 * 5, 250 - 47)
        draw_boss("Skeletron", 180 + 280 * 0 - 2, 250 * 2)
        draw_boss("Wall of Flesh", 180 + 280 * 1 + 25, 250 * 2 - 5)
        draw_boss("Queen Slime", 180 + 280 * 2 + 4, 250 * 2 + 53)
        if process_data['zenith_world']:
            draw_boss("Duke Fishron", 180 + 280 * 3, 250 * 2 + 70)
            draw_boss("Mechdusa", 180 + 280 * 4 + 80, 250 * 2 + 30)
            draw_boss("Plantera", 180 + 280 * 0 + 25, 250 * 3 + 30)
            draw_boss("Golem", 180 + 280 * 1 + 9, 250 * 3 + 30 - 47, -20)
            draw_boss("Empress of Light", 180 + 280 * 2 - 31, 250 * 3 + 30 + 21)
            draw_boss("Lunatic Cultist", 180 + 280 * 3 + 64, 250 * 3 + 30 + 92, 30)
            draw_boss("Moon Lord", 180 + 280 * 4 - 1, 250 * 3 + 30 + 4)
        else:
            draw_boss("The Destroyer", 180 + 280 * 3, 250 * 2 + 174, 50)
            draw_boss("The Twins", 180 + 280 * 4 + 23, 250 * 2 - 5)
            draw_boss("Skeletron Prime", 180 + 280 * 5 + 4, 250 * 2 - 4)
            draw_boss("Plantera", 180 + 280 * 0 + 25, 250 * 3 + 30)
            draw_boss("Golem", 180 + 280 * 1 + 9, 250 * 3 + 30 - 47, -20)
            draw_boss("Duke Fishron", 180 + 280 * 2, 250 * 3 + 30 + 27)
            draw_boss("Empress of Light", 180 + 280 * 3 - 31, 250 * 3 + 30 + 21)
            draw_boss("Lunatic Cultist", 180 + 280 * 4 + 63, 250 * 3 + 30 + 92, 30)
            draw_boss("Moon Lord", 180 + 280 * 5 - 20, 250 * 3 + 30 + 4)

        return img


if __name__ == '__main__':
    data = {"process":
        {
            "King Slime": False,
            "Pumpkin Moon": False,
            "Frost Moon": True,
            "Eye of Cthulhu": True,
            "Eater of Worlds or Brain of Cthulhu": False,
            "Eater of Worlds": False,
            "Brain of Cthulhu": True,
            "Queen Bee": True,
            "Deerclops": True,
            "Skeletron": True,
            "Wall of Flesh": False,
            "Queen Slime": True,
            "The Destroyer": True,
            "The Twins": True,
            "Skeletron Prime": False,
            "Plantera": False,
            "Golem": False,
            "Duke Fishron": False,
            "Empress of Light": False,
            "Lunatic Cultist": False,
            "Moon Lord": False,
            "Pillars": False,
            "Tower Stardust": True,
            "Tower Vortex": False,
            "Tower Nebula": True,
            "Tower Solar": False,
            "Goblins": True,
            "Pirates": False,
            "Frost": True,
            "Martians": False,
            "DD2InvasionT1": True,
            "DD2InvasionT2": True,
            "DD2InvasionT3": False
        },
        "kill_counts": {
            "King Slime": 1,
            "Eye of Cthulhu": 3,
            "Eater of Worlds": 5,
            "Brain of Cthulhu": 66,
            "Queen Bee": 3,
            "Deerclops": 4,
            "Skeletron": 32,
            "Wall of Flesh": 34,
            "Queen Slime": 4,
            "The Destroyer": 3,
            "The Twins": 4,
            "Skeletron Prime": 5,
            "Plantera": 7,
            "Golem": 5,
            "Duke Fishron": 4,
            "Empress of Light": 4,
            "Lunatic Cultist": 5,
            "Moon Lord": 9
        },
        "world_name": "啊da啊啊啊啊aaaaaa...",
        "drunk_world": False,
        "zenith_world": False,
        "world_icon": "IconHallowCrimsonNotTheBees",
        "group_id": 991556763
    }
    QueryProcess.get_process_png(data).show()
