from datetime import timedelta
from math import ceil
from typing import Optional, Tuple

from hoshino import Service, priv

sv = Service('calc_damage', bundle='pcr会战', enable_on_default=False, manage_priv=priv.SUPERUSER, help_='''
[计算 BOSS当前血量/第一刀伤害/第二刀伤害] 台服白嫖刀伤害计算(临时)
'''.strip())


def extract_plain_text(message: list) -> str:
    """提取纯文本"""
    text = []
    for msg_seg in message:
        if msg_seg.type == 'text' and msg_seg.data['text']:
            text.append(msg_seg.data['text'].strip())
    return ''.join(text)


def calc_damage(remain, damage1, damage2) -> str:
    """
    计算白嫖刀
    """
    remain -= damage1
    if remain <= 0:
        return '第一刀可以击杀BOSS'
    damage = damage2
    if remain - damage > 0:
        return '伤害不足，无法击杀BOSS'
    else:
        compensation_time = ceil(90 - remain / damage * 90 + 20)
        need = ceil(remain * 90 / 21)
        if compensation_time > 90:
            compensation_time = 90
        return f'击败返还时间{timedelta(seconds=compensation_time)}秒，满补至少需要造成{need}点伤害'


@sv.on_prefix(('calc', '白嫖刀', '算刀'))
async def calc(bot, ev):
    content = extract_plain_text(ev.message).split('/')
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
    msg = ['先出第一刀:']
    msg.append(calc_damage(remain, d1, d2))
    msg.append('先出第二刀:')
    msg.append(calc_damage(remain, d2, d1))
    await bot.send(ev, '\n'.join(msg))
