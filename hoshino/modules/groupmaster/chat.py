import random
import datetime
import re

from aiocqhttp.message import MessageSegment, unescape
from nonebot import on_command

from hoshino import R, Service, priv, util


# basic function for debug, not included in Service('chat')
@on_command(
    'zai?',
    aliases=(
        '在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'
    ),
    only_to_me=True
)
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')


sv = Service('chat', visible=False)


@sv.on_fullmatch('沙雕机器人')
async def say_sorry(bot, ev):
    await bot.send(ev, 'ごめんなさい！嘤嘤嘤(〒︿〒)')


@sv.on_fullmatch(('老婆', 'waifu', 'laopo'), only_to_me=True)
async def chat_waifu(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, R.img('laopo.jpg').cqcode)
    else:
        await bot.send(ev, 'mua~')


@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, '你给我滚！', at_sender=True)


@sv.on_fullmatch('mua', only_to_me=True)
async def chat_mua(bot, ev):
    await bot.send(ev, '笨蛋~', at_sender=True)


@sv.on_fullmatch('来点星奏')
async def seina(bot, ev):
    await bot.send(ev, R.img('星奏.png').cqcode)


# @sv.on_fullmatch(('我有个朋友说他好了', '我朋友说他好了', ))
# async def ddhaole(bot, ev):
#     await bot.send(ev, '那个朋友是不是你弟弟？')
#     await util.silence(ev, 30)

@sv.on_fullmatch(('可爱', '你好棒', '你真棒', '真厉害', '好聪明', '你真可爱', '真可爱'), only_to_me=True)
async def you_are_awesome(bot, ev):
    await bot.send(ev, '诶嘿嘿~~~')


@sv.on_fullmatch((('你好', '你好呀', '你好啊')), only_to_me=True)
async def greet(bot, ev):
    await bot.send(ev, '你好呀~', at_sender=True)


@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    await bot.send(ev, '不许好，憋回去！')
    await util.silence(ev, 30)


@sv.on_fullmatch(('早', '早安', '早上好', '早安哦', '早上好呀', '早呀', 'good morning'))
async def good_morning(bot, ev):
    now_hour = datetime.datetime.now().hour
    if 0 <= now_hour < 6:
        await bot.send(ev, f'好早! 现在才{now_hour}点!', at_sender=True)
    elif 6 <= now_hour < 10:
        await bot.send(ev, '早上好! 今天打算做什么呢?', at_sender=True)
    elif 21 <= now_hour < 24:
        await bot.send(ev, '早...嗯? 啊? 诶~~~~~~?', at_sender=True)
    else:
        await bot.send(ev, f'已经{now_hour}点了, 不早了哦~', at_sender=True)


@sv.on_fullmatch(('晚上好', '晚上好啊', '晚上好呀', 'good evening'))
async def good_evening(bot, ev):
    now_hour = datetime.datetime.now().hour
    if 18 <= now_hour < 24:
        await bot.send(ev, '晚上好! 今晚想做什么呢?', at_sender=True)
    elif 0 <= now_hour < 6:
        await bot.send(ev, f'{now_hour}点啦, 还不睡吗?', at_sender=True)
    elif 6 <= now_hour < 9:
        await bot.send(ev, '晚上好...嗯? 我刚起床呢', at_sender=True)
    else:
        await bot.send(ev, f'现在才{now_hour}点, 还不到晚上哦~', at_sender=True)


@sv.on_fullmatch(('晚安', '晚安哦', '晚安啦', 'good night'))
async def good_night(bot, ev):
    now_hour = datetime.datetime.now().hour
    if now_hour <= 3 or now_hour >= 21:
        await bot.send(ev, '晚安~', at_sender=True)
    elif 19 <= now_hour < 21:
        await bot.send(ev, f'诶? 现在才{now_hour}点, 这么早就要休息了吗?', at_sender=True)
    elif 3 <= now_hour < 5:
        await bot.send(ev, '你就是熬夜冠军吗?', at_sender=True)
    else:
        await bot.send(ev, f'现在才{now_hour}点, 再努力一会儿吧~(ง •_•)ง', at_sender=True)

# ============================================ #


@sv.on_keyword(('女装'), only_to_me=True)
async def womens_clothing(bot, ctx):
    await bot.send(ctx, '示范给我看看呀~', at_sender=True)


@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('确实.jpg').cqcode)


@sv.on_keyword(('会战'))
async def chat_clanba(bot, ctx):
    if random.random() < 0.02:
        await bot.send(ctx, R.img('我的天啊你看看都几度了.jpg').cqcode)


@sv.on_keyword(('内鬼'))
async def chat_neigui(bot, ctx):
    if random.random() < 0.10:
        await bot.send(ctx, R.img('内鬼.png').cqcode)

nyb_player = f'''{R.img('newyearburst.gif').cqcode}
正在播放：New Year Burst
──●━━━━ 1:05/1:30
⇆ ㅤ◁ ㅤㅤ❚❚ ㅤㅤ▷ ㅤ↻
'''.strip()


@sv.on_keyword(('春黑', '新黑'))
async def new_year_burst(bot, ev):
    if random.random() < 0.02:
        await bot.send(ev, nyb_player)


# ================ test ====================

@sv.on_fullmatch('test_rec')
async def test_rec(bot, ev):
    await bot.send(ev, R.rec('YUUDACHI/5.mp3').cqcode)


@sv.on_keyword('来啊快活啊', only_to_me=True)
async def get_out(bot, ctx):
    await bot.send(ctx, '爬' * random.randint(1, 8) + '!', at_sender=True)
    await util.silence(ctx, 30)


@sv.on_prefix('echo')
async def echo(bot, ev):
    context = []
    for msg_seg in ev.message:
        if msg_seg.type == 'text':
            context.append(msg_seg.data['text'].strip())
    if context:
        _type, _dict_text = re.match(
            r'\[CQ:(\w+),(.*)\]',
            unescape(''.join(context))
        ).groups()
        _dict = {}
        for item in _dict_text.split(','):
            item = item.split('=')
            k = item[0]
            v = ''.join(item[1:])
            _dict[k.strip()] = v.strip()
        await bot.send(ev, MessageSegment(type_=_type, data=_dict))


@sv.on_fullmatch('test_chat')
async def test_chat(bot, ev):
    msg = await bot.send(ev, '测试消息')
    import asyncio
    await asyncio.sleep(3)
    await util.delete_msg(ev, msg['message_id'])
