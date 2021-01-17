import json
import typing
from pathlib import Path

import aiocqhttp
from aiocqhttp.message import MessageSegment

from hoshino import Service, priv

sv = Service('farm', bundle='pcr会战', enable_on_default=False, manage_priv=priv.SUPERUSER, help_='''
[@bot 农场登记 @成员...] 登记去农场的成员
[@bot 农场登出 @成员...] 登记从农场回来的成员
[@bot 农场查询] 查询去了农场的成员
[@bot 农场广播] @通知在农场的成员回公会
[去农场:留言] 登记前往农场的信息并备注详情
[回公会:留言] 登记回到公会的信息并备注详情
[@bot 农场处理] 显示等待处理的列表
[@bot 农场处理完成] 结束处理并应用
'''.strip())

f_farm = Path().home() / Path('.hoshino/clantools/farm.json')
f_book = Path().home() / Path('.hoshino/clantools/farm_book.json')
f_back = Path().home() / Path('.hoshino/clantools/farm_back_book.json')

if not f_farm.exists():
    with f_farm.open('w') as f:
        json.dump({}, f, ensure_ascii=False)

if not f_book.exists():
    with f_book.open('w') as f:
        json.dump({}, f, ensure_ascii=False)

if not f_back.exists():
    with f_back.open('w') as f:
        json.dump({}, f, ensure_ascii=False)


def extract_target_members(message: list) -> typing.Union[list, str]:
    """提取目标成员"""
    targets = []
    for msg_seg in message:
        if msg_seg.type == 'at' and msg_seg.data['qq'] == 'all':
            return 'all'
        if msg_seg.type == 'at':
            targets.append(msg_seg.data['qq'])
    return targets


@sv.on_prefix(('农场登记', '农场添加'), only_to_me=True)
async def farm(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有群管理才可以登记~', at_sender=True)
        return
    user_id = extract_target_members(ev.message)
    if not user_id:
        await bot.send(ev, '请@你要登记的人~', at_sender=True)
        return
    elif user_id == 'all':
        await bot.send(ev, '不可以全部登记~')
        return
    else:
        user_id = list(map(lambda u: int(u), user_id))

    d_farm_object = {}
    with f_farm.open('r') as f:
        d_farm_object = json.load(f)

    gid = str(ev['group_id'])
    if gid not in d_farm_object:
        d_farm_object[gid] = []

    d_book_object = {}
    with f_book.open('r') as f:
        d_book_object = json.load(f)

    repeat = []
    for uid in user_id:
        if gid in d_book_object and str(uid) in d_book_object[gid]:
            del d_book_object[gid][str(uid)]
        if uid in d_farm_object[gid]:
            repeat.append(uid)
        else:
            d_farm_object[gid].append(uid)
    with f_farm.open('w') as f:
        json.dump(d_farm_object, f, ensure_ascii=False)
    with f_book.open('w') as f:
        json.dump(d_book_object, f, ensure_ascii=False)

    users = []
    for uid in user_id:
        try:
            users.append(await bot.get_group_member_info(group_id=gid, user_id=uid))
        except aiocqhttp.exceptions.ActionFailed:
            pass
    user_info = [f'{user["card"] if user["card"].strip() else user["nickname"]}({user["user_id"]})' for user in users]
    await bot.send(ev, f'以下成员已经登记到农场:\n{", ".join(user_info)}')


@sv.on_fullmatch(('农场查询', '谁在农场', '农场名单'), only_to_me=True)
async def farm_check(bot, ev):
    gid = str(ev['group_id'])
    d_farm_object = {}
    with f_farm.open('r') as f:
        d_farm_object = json.load(f)
    if gid in d_farm_object and d_farm_object[gid]:
        users = []
        unknow_id = []
        for uid in d_farm_object[gid]:
            try:
                users.append(await bot.get_group_member_info(group_id=gid, user_id=uid))
            except aiocqhttp.exceptions.ActionFailed:
                unknow_id.append(str(uid))
        if users:
            user_info = [f'{user["card"] if user["card"].strip() else user["nickname"]}({user["user_id"]})' for user in users]
            await bot.send(ev, f'以下成员正在务农中:\n{", ".join(user_info)}')
        if unknow_id:
            await bot.send(ev, f'以下农场成员可能已经不在群中:\n{", ".join(unknow_id)}')
    else:
        await bot.send(ev, '没有人在农场里~')


@sv.on_prefix(('农场登出', '移出农场', '农场删除'), only_to_me=True)
async def farm_back(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有群管理才可以登记~', at_sender=True)
        return
    user_id = extract_target_members(ev.message)
    if not user_id:
        await bot.send(ev, '请@你要登记的人~', at_sender=True)
        return
    elif user_id == 'all':
        await bot.send(ev, '不可以全部登记~')
        return
    else:
        user_id = list(map(lambda u: int(u), user_id))

    d_farm_object = {}
    with f_farm.open('r') as f:
        d_farm_object = json.load(f)
    
    gid = str(ev['group_id'])
    if gid not in d_farm_object:
        await bot.send(ev, '农场里没有人诶')
        return
    
    d_back_book_object = {}
    with f_back.open('r') as f:
        d_back_book_object = json.load(f)

    unknow_id = []
    remove = []
    for uid in user_id:
        if gid in d_back_book_object and str(uid) in d_back_book_object[gid]:
            del d_back_book_object[gid][str(uid)]
        if uid in d_farm_object[gid]:
            d_farm_object[gid].remove(uid)
            remove.append(uid)
        else:
            unknow_id.append(uid)
    with f_farm.open('w') as f:
        json.dump(d_farm_object, f, ensure_ascii=False)
    with f_back.open('w') as f:
        json.dump(d_back_book_object, f, ensure_ascii=False)

    users = []
    if remove:
        for uid in remove:
            try:
                users.append(await bot.get_group_member_info(group_id=gid, user_id=uid))
            except aiocqhttp.exceptions.ActionFailed:
                unknow_id.append(str(uid))
        user_info = [f'{user["card"] if user["card"].strip() else user["nickname"]}({user["user_id"]})' for user in users]
        await bot.send(ev, f'以下成员已经从农场中移除:\n{", ".join(user_info)}')
    if unknow_id:
        await bot.send(ev, f'以下成员可能不在农场中或已经不在群中:\n{", ".join(unknow_id)}')


@sv.on_fullmatch(('农场广播', '农场通知', '农场召回'), only_to_me=True)
async def farm_bc(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有群管理才可以召回成员~', at_sender=True)
        return

    d_farm_object = {}
    with f_farm.open('r') as f:
        d_farm_object = json.load(f)
    
    gid = str(ev['group_id'])
    if gid not in d_farm_object:
        await bot.send(ev, '农场里没有人诶')
        return
    else:
        l_uid = d_farm_object[gid]
        msg = [str(MessageSegment.at(user_id=uid)) for uid in l_uid]
        await bot.send(ev, f'{"".join(msg)} 是时候从农场回来啦!')


@sv.on_prefix(('去农场'))
async def farm_book(bot ,ev):
    message = ev.message.extract_plain_text().strip()
    if message.startswith(':') or message.startswith('：'):
        message = message[1:]
    else:
        return

    uid = str(ev['user_id'])
    gid = str(ev['group_id'])

    d_book_object = {}
    with f_book.open('r') as f:
        d_book_object= json.load(f)
    
    if gid not in d_book_object:
        d_book_object[gid] = {}

    update = False
    if uid in d_book_object[gid]:
        update = True
    d_book_object[gid][uid] = message

    with f_book.open('w') as f:
        json.dump(d_book_object, f, ensure_ascii=False)

    await bot.send(ev, f'{"登记成功" if not update else "更新成功"}, 您的留言是 {message}, 请耐心等待管理员处理')


@sv.on_prefix(('回公会', '回工会'))
async def farm_back_book(bot ,ev):
    message = ev.message.extract_plain_text().strip()
    if message.startswith(':') or message.startswith('：'):
        message = message[1:]
    else:
        return

    uid = ev['user_id']
    gid = str(ev['group_id'])

    d_farm_object = {}
    with f_farm.open('r') as f:
        d_farm_object = json.load(f)
    
    if gid not in d_farm_object or uid not in d_farm_object[gid]:
        await bot.send(ev, '你不在农场中, 不需要登记回归', at_sender=True)
        return

    d_back_book_object = {}
    with f_back.open('r') as f:
        d_back_book_object= json.load(f)
    
    if gid not in d_back_book_object:
        d_back_book_object[gid] = {}

    update = False
    if str(uid) in d_back_book_object[gid]:
        update = True

    d_back_book_object[gid][str(uid)] = message

    with f_back.open('w') as f:
        json.dump(d_back_book_object, f, ensure_ascii=False)

    await bot.send(ev, f'{"登记成功" if not update else "更新成功"}, 您的留言是 {message}, 请耐心等待管理员处理')


@sv.on_fullmatch(('农场处理', '处理农场'), only_to_me=True)
async def farm_book_list(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有群管理才可以处理~', at_sender=True)
        return
    gid = str(ev['group_id'])
    msg = []

    # get book list
    d_book_object = {}
    with f_book.open('r') as f:
        d_book_object= json.load(f)
    
    if gid not in d_book_object and d_book_object[gid]:
        d_book_object[gid] = {}
    elif gid in d_book_object and d_book_object[gid]:
        msg.append('预约去农场的成员:')

    for uid, message in d_book_object[gid].items():
        try:
            user = await bot.get_group_member_info(group_id=gid, user_id=uid)
            msg.append(f'{user["card"] if user["card"].strip() else user["nickname"]}({user["user_id"]}): {message if message else "无留言"}')
        except aiocqhttp.exceptions.ActionFailed:
            pass

    # get book back list
    d_back_book_object = {}
    with f_back.open('r') as f:
        d_back_book_object= json.load(f)
    
    if gid not in d_back_book_object:
        d_back_book_object[gid] = {}
    else:
        msg.append('预约回公会的成员:')

    for uid, message in d_back_book_object[gid].items():
        try:
            user = await bot.get_group_member_info(group_id=gid, user_id=uid)
            msg.append(f'{user["card"] if user["card"].strip() else user["nickname"]}({user["user_id"]}): {message if message else "无留言"}')
        except aiocqhttp.exceptions.ActionFailed:
            pass

    if len(msg) > 1:
        msg.append('发送at我发送【农场处理完成】将自动清空列表，若要单独处理成员，请使用【农场登记/登出】')
        await bot.send(ev, '\n'.join(msg))
    else:
        await bot.send(ev, '没有需要处理的项目')


@sv.on_fullmatch(('农场处理完成'), only_to_me=True)
async def farm_process_done(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有群管理才可以操作~', at_sender=True)
        return
    d_farm = []
    d_book = {}
    d_back = {}
    with f_farm.open('r') as f:
        d_farm = json.load(f)
    with f_book.open('r') as f:
        d_book = json.load(f)
    with f_back.open('r') as f:
        d_back = json.load(f)
    
    gid = str(ev.group_id)
    l_farm = d_farm[gid] if gid in d_farm else []
    l_book = d_book[gid].keys() if gid in d_book else []
    l_back = d_back[gid].keys() if gid in d_back else []
    l_book = list(map(lambda x: int(x), l_book))
    l_back = list(map(lambda x: int(x), l_back))

    l_in = []
    l_out = []
    for uid in l_book:
        if uid not in l_farm:
            l_farm.append(uid)
            l_in.append(uid)
    for uid in l_back:
        if uid in l_farm:
            l_farm.remove(uid)
            l_out.append(uid)

    d_farm[gid] = l_farm
    d_book[gid] = {}
    d_back[gid] = {}

    with f_farm.open('w') as f:
        json.dump(d_farm, f, ensure_ascii=False)
    with f_book.open('w') as f:
        json.dump(d_book, f, ensure_ascii=False)
    with f_back.open('w') as f:
        json.dump(d_back, f, ensure_ascii=False)
    
    l_user_in = []
    l_user_out = []
    for uid in l_in:
        try:
            user = await bot.get_group_member_info(group_id=gid, user_id=uid)
            l_user_in.append(f'{user["card"] if user["card"].strip() else user["nickname"]}({user["user_id"]})')
        except aiocqhttp.exceptions.ActionFailed:
            pass

    for uid in l_out:
        try:
            user = await bot.get_group_member_info(group_id=gid, user_id=uid)
            l_user_out.append(f'{user["card"] if user["card"].strip() else user["nickname"]}({user["user_id"]})')
        except aiocqhttp.exceptions.ActionFailed:
            pass
    
    msg = []
    if l_user_in:
        msg.append('以下成员已登记到农场:')
        msg.append(', '.join(l_user_in))
    if l_user_out:
        msg.append('以下成员已登出农场:')
        msg.append(', '.join(l_user_out))
    await bot.send(ev, '\n'.join(msg))
