import datetime
import random

import aiohttp
from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from src.models.group import Group
from src.utils.sensitive_words_filter import SensitiveWordsFilter
from src.utils.text_handler import TextHandle
from src.models.user import User


def msg_cut(msg: str) -> list:
    msg = msg.split(" ")
    msg = [word for word in msg if word]
    return msg


def paginate(data, page_size, page_number):
    # 计算开始和结束的索引
    start = (page_number - 1) * page_size
    end = start + page_size
    # 返回分页后的数据
    return data[start:end]


cai_sentences = [
    ("???", "告诉你，我的实力凌驾于你之上。"),
    ("???", "谁来我的私人服务器？"),
    ("???", "告诉你，我的实力凌驾于你之上。"),
    ("???", "我在别的服打着打着一下两三百铂金币。"),
    ("Ezfic", "桑百颗够吗?"),
    ("泰拉剑人", "关键我态度挺好的呀!"),
    ("Fr", "你见不到国内有泰拉服务器了,这款游戏在国内我会代理下来。")
]


async def get_hitokoto() -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://oiapi.net/API/AWord", ssl=False) as response:
                data = await response.json()
                if data['data']['from'] == "" or len(data['message'].splitlines())>4:
                    cai_sentence = random.choice(cai_sentences)
                    sentence = (f"{cai_sentence[1]}\n"
                                f"—— {cai_sentence[0]}")
                else:
                    sentence = (f"{data['message']}\n"
                                f"—— {data['data']['from']}")

                return sentence
    except Exception as ex:
        print(ex)
        return (f"你的名言貌似走丢了捏~\n"
               f"—— Cai")


bind = on_command("添加白名单", aliases={"绑定"})


@bind.handle()
async def bind_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    user = User.get_user(group.open_id, event.author.union_openid)
    if user is not None and user.name != "":
        await bind.finish(f'\n『白名单』\n' +
                          f"你已经在本群绑定过白名单了哦！\n"
                          f"你绑定的角色为[{user.name}]\n"
                          f"TIPS: 可以使用'修改白名单 <名字>'重绑哦~")
    if len(msg) != 2:
        await bind.finish(f'\n『白名单』\n' +
                          f"格式错误！\n"
                          f"正确格式: 添加白名单 <名字>")
    user2 = User.get_user_by_name(event.group_openid, msg[1])
    if user2 is not None:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"这个名字被占用啦！")

    if len(msg[1]) > 15:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字最大长度不难超过15字符！")

    if not TextHandle.check_name(msg[1]):
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字只能含汉字、字母、数字哦！")
    if SensitiveWordsFilter.check(msg[1]):
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"包含违禁词！")

    if not msg[1]:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字不能为空！")
    if user is not None:
        user.name = msg[1]
        user.update()
    else:
        User.add_user(group.open_id, event.author.union_openid, msg[1])

    await bind.finish(f'\n『白名单』\n' +
                      f"绑定成功~\n"
                      f"你可以使用[{msg[1]}]进入服务器啦!")


rebind = on_command("修改白名单", aliases={"更改白名单"}, force_whitespace=True)


@rebind.handle()
async def rebind_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    user = User.get_user(group.open_id, event.author.union_openid)
    if user is None or user.name == "":
        await rebind.finish(f'\n『白名单』\n' +
                            f"你还没有在本群这里过白名单哦！\n"
                            f"发送'/添加白名单 <名字>'可以进行绑定")
    now = datetime.datetime.today().date()

    days_since_last_rename = (now - user.last_rename.date()).days

    if days_since_last_rename < 3:
        days_left = 3 - days_since_last_rename
        next_rename_date = now + datetime.timedelta(days=days_left)
        await rebind.finish(f'\n『白名单』\n' +
                            f"检测到你在这个月修改过一次白名单~\n" +
                            f"{days_left}天之后, 即{next_rename_date}才可以继续修改")
    if len(msg) != 2:
        await rebind.finish(f'\n『白名单』\n' +
                            f"格式错误！\n"
                            f"正确格式: 修改白名单 <名字>")
    user2 = User.get_user_by_name(event.group_openid, msg[1])
    if user2 is not None:
        await rebind.finish(f'\n『白名单』\n' +
                            f"绑定失败!\n"
                            f"这个名字被占用啦！")

    if len(msg[1]) > 15:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字最大长度不难超过15字符！")

    if not TextHandle.check_name(msg[1]):
        await rebind.finish(f'\n『白名单』\n' +
                            f"绑定失败!\n"
                            f"名字只能含汉字、字母、数字哦！")
    if SensitiveWordsFilter.check(msg[1]):
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"包含违禁词！")

    if not msg[1]:
        await rebind.finish(f'\n『白名单』\n' +
                            f"绑定失败!\n"
                            f"名字不能为空！")
    user.name = msg[1]
    user.last_rename = datetime.datetime.now()
    user.update()
    await rebind.finish(f'\n『白名单』\n' +
                        f"重绑成功~\n"
                        f"你可以使用[{msg[1]}]进入服务器啦!\n"
                        f"TIPS： CaiBot不会自动迁移存档哦~")


# un_bind = on_command("删除白名单", force_whitespace=True)
#
#
# @un_bind.handle()
# async def un_bind_handle(event: GroupAtMessageCreateEvent):
#     msg = msg_cut(event.get_plaintext())
#     if event.author.union_openid == 3042538328:
#         if len(msg) != 2:
#             await un_bind.finish(MessageSegment.at(event.author.union_openid) +
#                                  f'\n『白名单』\n' +
#                                  "格式错误！\n"
#                                  f"正确格式: 删除白名单 <名字>")
#         user = User.get_user_name(msg[1])
#         if user is not None:
#             user.name = ""
#             user.update()
#             await un_bind.finish(MessageSegment.at(event.author.union_openid) +
#                                  f'\n『白名单』\n' +
#                                  "解绑成功!\n"
#                                  f"QQ:{user.open_id},处于未绑定状态")
#         else:
#             await un_bind.finish(MessageSegment.at(event.author.union_openid) +
#                                  f'\n『白名单』\n' +
#                                  "没有找到玩家!")


sign = on_command("签到", force_whitespace=True)


@sign.handle()
async def sign_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    user = User.get_user(group.open_id, event.author.union_openid)
    if user is None:
        await sign.finish(f'\n『签到』\n' +
                          f"你还没有添加白名单！\n"
                          f"发送'/添加白名单 <名字>'来添加白名单")

    def is_today_or_yesterday(dt):
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        return dt.date() in [today, yesterday]

    def is_today(date):
        today = datetime.datetime.now()
        return date.date() == today.date()

    if is_today(user.last_sign):
        await sign.finish(f'\n『签到』\n' +
                          f"你今天已经签过到了哦!\n"
                          f"明天再来吧~")
    if is_today_or_yesterday(user.last_sign):
        user.sign_count += 1
    else:
        user.sign_count = 1
    luck = random.randint(0, 100)
    sign_money = random.randint(0, 1000)
    user.money += int(sign_money * (luck / 100 + 1) + user.sign_count * 10)
    if user.last_sign.date() == datetime.datetime.today().date():
        await sign.finish(f'\n『签到』\n' +
                          f"摸摸头,今天你已经签过到了哦!\n"
                          f"明天再来吧~")
    if datetime.datetime.now().hour < 12:
        time_text = "上午好"
    elif datetime.datetime.now().hour == 12:
        time_text = "中午好"
    elif 12 < datetime.datetime.now().hour < 18:
        time_text = "下午好"
    else:
        time_text = "晚上好"
    day = user.sign_count
    text_list = [f"{time_text}呀,今天是你连续签到的第{day}天,额外获得{day * 10}金币",
                 f"{time_text}阁下,今天是你连续签到的第{day}天,额外获得{day * 10}金币",
                 f"{time_text},今天是阁下连续签到的第{day}天,额外获得{day * 10}金币"]
    text = text_list[random.randint(0, 2)]
    user.last_sign = datetime.datetime.now()
    user.update()

    await sign.finish(f'\n『签到』\n' +
                      f"{text}\n"
                      f"今日人品:{luck}\n"
                      f"金币加成:+{luck}%\n"
                      f"获得金币: {int(sign_money * (luck / 100 + 1) + user.sign_count * 10)}\n"
                      f"签到排名: {User.get_sign_rank(group.open_id)}\n\n"
                      f"{await get_hitokoto()}")


bank = on_command("查询金币", force_whitespace=True)


@bank.handle()
async def bank_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    user = User.get_user(group.open_id, event.author.union_openid)
    if user is None:
        await bank.finish(f'\n『银行』\n' +
                          f"你还没有添加白名单！\n"
                          f"发送'/添加白名单 <名字>'来添加白名单")
    await bank.finish(f'\n『银行』\n' +
                      f"金币: {user.money}\n"
                      f"连签天数: {user.sign_count}")


find_player = on_command("查绑定", aliases={"查询绑定", "绑定查询"}, force_whitespace=True)


@find_player.handle()
async def find_player_function(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) >= 2:
        user = None
        # noinspection PyBroadException
        try:
            user = User.get_user(group.open_id, msg[1])
        except:
            pass
        user2 = User.get_user_by_name(event.group_openid, msg[1])

        if user is None and user2 is None:
            await find_player.finish(f"\n『查绑定』\n"
                                     f"查询失败！\n"
                                     f"没有找到与[{msg[1]}]有关的信息")

        if user is not None and user2 is not None:
            await find_player.finish(f"\n『查绑定』\n"
                                     f"查询成功！\n"
                                     f"#️⃣OpenID[{user.open_id}]\n"
                                     f"绑定角色[{user.name}]\n"
                                     f"#️⃣OpenID[{user2.open_id}]\n"
                                     f"绑定角色[{user2.name}]")
        if user is not None:
            await find_player.finish(f"\n『查绑定』\n"
                                     f"查询成功！\n"
                                     f"#️⃣OpenID[{user.open_id}]\n"
                                     f"绑定角色[{user.name}]")
        if user2 is not None:
            await find_player.finish(f"\n『查绑定』\n"
                                     f"查询成功！\n"
                                     f"#️⃣OpenID[{user2.open_id}]\n"
                                     f"绑定角色[{user2.name}]")
    else:
        await find_player.finish("\n『查绑定』\n"
                                 "格式错误！\n"
                                 "正确格式：查绑定 [角色名字]/[OpenID]")
