import json
import typing
from pathlib import Path

from hoshino import MessageSegment, Service, priv

farm_file = Path().home() / Path('.hoshino/farm.json')

if not farm_file.exists():
    with farm_file.open('w') as f:
        json.dump([], f, ensure_ascii=False)

sv = Service('farm', bundle='pcr农场', enable_on_default=False, manage_priv=priv.SUPERUSER, help_='''
[@bot 农场登记 @成员...] 登记去农场的成员
[@bot 农场登出 @成员...] 登记从农场回来的成员
[@bot 农场查询] 查询去了农场的成员
'''.strip())


def extract_target_members(message: list) -> typing.Union[list, str]:
    """提取目标成员"""
    targets = []
    for msg_seg in message:
        if msg_seg.type == 'at' and msg_seg.data['qq'] == 'all':
            return 'all'
        if msg_seg.type == 'at':
            targets.append(msg_seg.data['qq'])
    return targets


@sv.on_prefix(('农场登记'), only_to_me=True)
async def farm(bot, ev):
    user_list = []
    with farm_file.open('r') as f:
        user_list = json.load(f)
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
    for uid in user_id:
        if uid in user_list:
            await bot.send(ev, MessageSegment.at(user_id=uid) + '已经登记过了')
        else:
            user_list.append(uid)
    with farm_file.open('w') as f:
        json.dump(user_list, f, ensure_ascii=False)
    await bot.send(ev, '登记完成咯~')


@sv.on_prefix(('农场查询'), only_to_me=True)
async def farm_check(bot, ev):
    user_list = []
    with farm_file.open('r') as f:
        user_list = json.load(f)
    if user_list:
        await bot.send(ev, ''.join([f'{MessageSegment.at(u_id)}' for u_id in user_list]) + '正在务农中~')
    else:
        await bot.send(ev, '没有人在农场里~')


@sv.on_prefix(('农场登出'), only_to_me=True)
async def farm_back(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有群管理才可以登记~', at_sender=True)
        return
    user_list = []
    with farm_file.open('r') as f:
        user_list = json.load(f)
    user_id = extract_target_members(ev.message)
    if not user_id:
        await bot.send(ev, '请@你要登记的人~', at_sender=True)
        return
    elif user_id == 'all':
        await bot.send(ev, '不可以全部登记~')
        return
    else:
        user_id = list(map(lambda u: int(u), user_id))
    for uid in user_id:
        if uid in user_list:
            user_list.remove(uid)
        else:
            await bot.send(ev, MessageSegment.at(user_id=uid) + '不在农场里')
    with farm_file.open('w') as f:
        json.dump(user_list, f, ensure_ascii=False)
    await bot.send(ev, '登记完成咯~')
