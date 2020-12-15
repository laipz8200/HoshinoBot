import json
from datetime import timedelta
from math import ceil
from pathlib import Path

from hoshino import Service, priv

sv = Service('calc_damage', bundle='pcr会战', enable_on_default=False, manage_priv=priv.SUPERUSER, help_='''
[算刀 cn/tw 绑定公会服务器] 
[算刀 BOSS当前血量/第一刀伤害/第二刀伤害] 陆/台服白嫖刀伤害计算(临时)
'''.strip())

save = Path().home() / Path('.hoshino/clantools/calc-damage.json')
save.parent.mkdir(parents=True, exist_ok=True)


def calc_damage(remain: int, damage1: int, damage2: int, server: str) -> str:
    """
    计算白嫖刀
    """
    remain -= damage1
    if remain <= 0:
        return '第一刀可以击杀BOSS'
    damage = damage2
    if remain - damage > 0:
        return '伤害不足，无法击杀BOSS'
    if server == 'tw':
        compensation_time = ceil(90 - remain / damage * 90 + 20)
        need = ceil(remain * 90 / 21)
        if compensation_time > 90:
            compensation_time = 90
        return f'击败返还时间{timedelta(seconds=compensation_time)}秒，满补至少需要造成{need}点伤害'
    else:
        compensation_time = ceil(90 - remain / damage * 90 + 10)
        need = ceil(remain * 90 / 11)
        if compensation_time > 90:
            compensation_time = 90
        return f'击败返还时间{timedelta(seconds=compensation_time)}秒，满补至少需要造成{need}点伤害'


def bind_server(gid: str, server: str):
    servers = {}
    if save.exists():
        with save.open('r') as f:
            servers = json.load(f)
    servers[gid] = server
    with save.open('w') as f:
        json.dump(servers, f)


@sv.on_prefix(('calc', '白嫖刀', '算刀'))
async def calc(bot, ev):
    gid = str(ev['group_id'])
    content = str(ev.message.extract_plain_text())
    if 'cn' in content:
        bind_server(gid, 'cn')
        await bot.send(ev, '绑定成功')
        return
    elif 'tw' in content or 'jp' in content:
        bind_server(gid, 'tw')
        await bot.send(ev, '绑定成功')
        return
    else:
        content = content.split('/')
    sv.logger.info(f'{content=}')
    if not content[0]:
        await bot.send(ev, '请输入[算刀]BOSS当前血量/第一刀伤害/第二刀伤害')
        return
    try:
        content = list(map(lambda x: int(x), content))
        if len(content) != 3:
            await bot.send(ev, '只能输入三项数值')
            return
    except Exception:
        await bot.send(ev, '请输入正整数')
        return
    remain, d1, d2 = content
    if remain <= 0:
        await bot.send(ev, 'BOSS血量必须为正整数')
        return
    if d1 < 0 or d2 < 0:
        await bot.send(ev, '伤害数值不能为负数')
        return
    with save.open('r') as f:
        servers = json.load(f)
    if not servers or gid not in servers:
        await bot.send(ev, '请先绑定服务器')
        return
    server = servers[gid]
    msg = ['先出第一刀:']
    msg.append(calc_damage(remain, d1, d2, server))
    msg.append('先出第二刀:')
    msg.append(calc_damage(remain, d2, d1, server))
    await bot.send(ev, '\n'.join(msg))
