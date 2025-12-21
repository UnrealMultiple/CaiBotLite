import random
from datetime import datetime, timedelta
from typing import List

import httpx
from nonebot import on_command, logger
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from caibotlite.constants import WhiteList
from caibotlite.dependencies import Args, CurrentGroup, Session
from caibotlite.managers import GroupManager, UserManager
from caibotlite.models import User
from caibotlite.utils import check_text_ok

bind = on_command("添加白名单", aliases={"绑定"}, force_whitespace=True, block=True)


@bind.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)
    if user is not None and user.name != "" and user.name != None:
        await bind.finish(f'\n『白名单』\n' +
                          f"你已经在本群绑定过白名单了哦！\n"
                          f"你绑定的角色为[{user.name}]\n"
                          f"TIPS: 可以使用\"/修改白名单 <名字>\"重绑哦~")
    if len(args) != 1:
        await bind.finish(f'\n『白名单』\n' +
                          f"格式错误！\n"
                          f"正确格式: 添加白名单 <名字>")
    name = args[0]

    user2 = await UserManager.get_user_by_name(session, group.open_id, name)

    if user2 is not None:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"这个名字被占用啦！")

    if len(name) > WhiteList.MAX_NAME_LENGTH:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字最大长度不难超过15字符！")

    if not UserManager.check_name_ok(name):
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字只能含汉字、字母、数字哦！")

    if not check_text_ok(name):
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"包含违禁词！")

    if user is not None:
        user.name = name
        await UserManager.update_user(session, user)
    else:
        await UserManager.create_user(session, group.open_id, event.author.union_openid, name)

    await bind.finish(f'\n『白名单』\n' +
                      f"绑定成功~\n"
                      f"你可以使用[{name}]进入服务器啦!")


rebind = on_command("修改白名单", aliases={"更改白名单"}, force_whitespace=True, block=True)


@rebind.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)
    if user is None or user.name == "":
        await rebind.finish(f'\n『白名单』\n' +
                            f"你还没有在本群这里过白名单哦！\n"
                            f"发送\"/添加白名单 <名字>\"可以进行绑定")
    now = datetime.now().date()
    days_since_last_rename = (now - user.last_rename.date()).days

    if days_since_last_rename < 3:
        days_left = 3 - days_since_last_rename
        next_rename_date = now + timedelta(days=days_left)
        await rebind.finish(f'\n『白名单』\n' +
                            f"检测到你在最近修改过一次白名单~\n" +
                            f"{days_left}天之后, 即{next_rename_date}才可以继续修改")

    if len(args) != 1:
        await rebind.finish(f'\n『白名单』\n' +
                            f"格式错误！\n"
                            f"正确格式: 修改白名单 <名字>")
    name = args[0]

    user2 = await UserManager.get_user_by_name(session, group.open_id, name)

    if user2 is not None:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"这个名字被占用啦！")

    if len(name) > WhiteList.MAX_NAME_LENGTH:
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字最大长度不难超过15字符！")

    if not UserManager.check_name_ok(name):
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"名字只能含汉字、字母、数字哦！")

    if not check_text_ok(name):
        await bind.finish(f'\n『白名单』\n' +
                          f"绑定失败!\n"
                          f"包含违禁词！")

    user.name = name
    user.last_rename = datetime.now().today()
    await UserManager.update_user(session, user)
    await rebind.finish(f'\n『白名单』\n' +
                        f"重绑成功~\n"
                        f"你可以使用[{name}]进入服务器啦!\n"
                        f"TIPS: CaiBot不会自动迁移存档哦~")


unbind = on_command("删除白名单", force_whitespace=True, block=True)


@unbind.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await unbind.finish(f'\n『白名单』\n' +
                            f"没有权限!\n"
                            f"只允许BOT管理员使用")
    if len(args) != 1:
        await unbind.finish(f'\n『白名单』\n' +
                            f"格式错误！\n"
                            f"正确格式: 删除白名单 <名字>")

    name = args[0]

    user = await UserManager.get_user_by_name(session, group.open_id, name)
    if user is not None:
        user.name = None
        await UserManager.update_user(session, user)
        await unbind.finish(f'\n『白名单』\n' +
                            f"删除成功!")
    else:
        await unbind.finish(f'\n『白名单』\n' +
                            "没有找到玩家!")


CAI_SENTENCES = [
    ("???", "告诉你，我的实力凌驾于你之上。"),
    ("???", "我在别的服打着打着一下两三百铂金币。"),
    ("Ezfic", "桑百颗够吗?"),
    ("泰拉剑人", "关键我态度挺好的呀!"),
    ("FR", "你见不到国内有泰拉服务器了,这款游戏在国内我会代理下来。"),
    ("???", "你记住\n"
            "哪天你再泰圈混不下去\n"
            "随时来找我"),
    ("妮妮", "关你屁事"),
    ("妮妮", "这是我的评论区，我让你滚你就得滚"),
    ("???", "克眼把数值拉上去和猪鲨差不多了"),
    ("清风", "你等着吧，反正总有一天我会成为泰拉瑞亚唯一的211、985"),
    ("???", "谁有时间读你们的破文档"),
    ("Caigito", "我没说若只可以聊天"),
    ("Poooo", "没有我实在是太可惜了"),
    ("???", "泰拉瑞亚作为沙盒三巨头属于是可玩性最低的了\n"
            "2D，世界大小限制，boss攻击单一\n"
            "真的boss不是冲撞就是弹幕")

]


async def get_hitokoto() -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://oiapi.net/API/AWord")
            data = response.json()
            if data['data']['from'] == "" or len(data['message'].splitlines()) > 4:
                cai_sentence = random.choice(CAI_SENTENCES)
                sentence = (f"{cai_sentence[1]}\n"
                            f"—— {cai_sentence[0]}")
            else:
                sentence = (f"{data['message']}\n"
                            f"—— {data['data']['from']}")
            return sentence
    except Exception as ex:
        logger.error(f"获取签到名言时出错: {ex}")
        return (f"你的名言貌似走丢了捏~\n"
                f"—— Cai")


sign = on_command("签到", force_whitespace=True, block=True)


@sign.handle()
async def _(event: GroupAtMessageCreateEvent, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)
    if user is None:
        await sign.finish(f'\n『签到』\n' +
                          f"你还没有添加白名单！\n"
                          f"发送\"/添加白名单 <名字>\"来添加白名单")

    if (sign_rank := await UserManager.sign(session, user)) is None:
        await sign.finish(f'\n『签到』\n' +
                          f"你今天已经签过到了哦!\n"
                          f"明天再来吧~")

    luck = random.randint(0, 100)
    sign_money = random.randint(group.config.min_sign_coins, group.config.max_sign_coins)
    got_money = int(sign_money * (luck / 100 + 1) + user.sign_consistency * 10)
    user.money += got_money
    await UserManager.update_user(session, user)

    match datetime.now().hour:
        case hour if 5 < hour < 12:
            time_text = "早上好"
        case 12:
            time_text = "中午好"
        case hour if 12 < hour < 18:
            time_text = "下午好"
        case _:
            time_text = "晚上好"

    day = user.sign_consistency
    head_list = [f"{time_text}呀,今天是你连续签到的第{day}天,额外获得{day * 10}金币",
                 f"{time_text}阁下,今天是你连续签到的第{day}天,额外获得{day * 10}金币",
                 f"{time_text},今天是阁下连续签到的第{day}天,额外获得{day * 10}金币"]

    head = random.choice(head_list)

    await sign.finish(f'\n『签到』\n' +
                      f"{head}\n"
                      f"今日人品: {luck}\n"
                      f"金币加成: +{luck}%\n"
                      f"获得金币: {got_money}\n"
                      f"签到排名: {sign_rank}\n\n"
                      f"{await get_hitokoto()}")


bank = on_command("查询金币", force_whitespace=True, block=True)


@bank.handle()
async def _(event: GroupAtMessageCreateEvent, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)

    if user is None:
        await bank.finish(f'\n『银行』\n' +
                          f"你还没有添加白名单！\n"
                          f"发送\"/添加白名单 <名字>\"来添加白名单")

    await bank.finish(f'\n『银行』\n' +
                      f"金币: {user.money}\n"
                      f"连签天数: {user.sign_consistency}\n"
                      f"签到天数: {user.sign_days}")


find_player = on_command("查绑定", aliases={"查询绑定", "绑定查询"}, force_whitespace=True, block=True)


@find_player.handle()
async def _(args: Args, group: CurrentGroup, session: Session):
    if len(args) == 0:
        await find_player.finish("\n『查绑定』\n"
                                 "格式错误！\n"
                                 "正确格式：查绑定 [角色名字]/[OpenID]/[UserID]")
    target = args[0]

    users = []
    if user := await UserManager.get_user_by_open_id(session, group.open_id, target):
        users.append(user)
    if user := await UserManager.get_user_by_name(session, group.open_id, target):
        users.append(user)
    if user := await UserManager.get_user_by_id(session, target):
        users.append(user)

    unique_users: List[User] = []
    seen = set()
    for user in users:
        if user.open_id not in seen:
            seen.add(user.open_id)
            unique_users.append(user)

    if not unique_users:
        await find_player.finish(f"\n『查绑定』\n"
                                 f"查询失败！\n"
                                 f"没有找到与[{target}]有关的信息")

    message = "\n『查绑定』\n查询成功！\n"
    for user in unique_users:
        message += f"#️⃣OpenID[{user.open_id}] (ID: {user.id})\n绑定角色[{user.name}]\n"

    await find_player.finish(message)
