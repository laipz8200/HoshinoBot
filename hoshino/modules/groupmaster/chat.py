import datetime
import random
import re

from aiocqhttp.message import MessageSegment, unescape
from nonebot import on_command

from hoshino import R, Service, get_bot, priv, util, logger
from hoshino.config import SUBSCRIBER, SUBSCRIBER_GROUP
from hoshino.typing import NoticeSession


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


def extract_plain_text(message: list) -> str:
    """提取纯文本"""
    text = []
    for msg_seg in message:
        if msg_seg.type == 'text' and msg_seg.data['text']:
            text.append(msg_seg.data['text'].strip())
    return ''.join(text)


def extract_target_members(message: list) -> str:
    """提取目标成员"""
    targets = []
    for msg_seg in message:
        if msg_seg.type == 'at' and msg_seg.data['qq'] == 'all':
            return 'all'
        if msg_seg.type == 'at':
            targets.append(msg_seg.data['qq'])
    return targets

# ============================================ #


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


@sv.on_fullmatch(((
    '你是猪', 'baka', 'bakabot', '你爹是大猪头'
)), only_to_me=True)
async def scolded(bot, ev):
    await util.silence(ev, 5*60, skip_su=False)
    await bot.send(ev, '哼~!', at_sender=True)


@sv.on_fullmatch('ghs')
async def ghs(bot, ev):
    await bot.send(ev, '干好事')


@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    await bot.send(ev, '不许好，憋回去！')
    await util.silence(ev, 30)


@sv.on_fullmatch((
    '早', '早安', '早上好', '早安哦', '早上好呀',
    '早呀', '早啊', '早啊早啊', 'good morning', '大家早'
))
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


@sv.on_fullmatch(('中午好', '午好', 'good afternoon'))
async def good_afternoon(bot, ev):
    now_hour = datetime.datetime.now().hour
    if 12 <= now_hour < 14:
        await bot.send(ev, '中午好呀', at_sender=True)
    else:
        await bot.send(ev, '现在可不是中午哦', at_sender=True)


@sv.on_fullmatch(('午安'))
async def wuan(bot, ev):
    now_hour = datetime.datetime.now().hour
    if 12 <= now_hour < 14:
        await bot.send(ev, '中午要好好休息哦', at_sender=True)
    else:
        await bot.send(ev, '现在可不是中午哦', at_sender=True)


@sv.on_fullmatch(('下午好'))
async def xiawuhao(bot, ev):
    now_hour = datetime.datetime.now().hour
    if 14 <= now_hour < 18:
        await bot.send(ev, '下午好! 要继续努力哟~', at_sender=True)
    elif 18 <= now_hour < 24:
        await bot.send(ev, f'{now_hour}点啦, 已经是晚上了哦', at_sender=True)
    elif 6 <= now_hour < 15:
        await bot.send(ev, '还不到下午呢, 清醒一点啦~', at_sender=True)
    else:
        await bot.send(ev, f'唔...你不用睡觉的吗?', at_sender=True)


@sv.on_fullmatch((
    '晚好', '晚上好', '晚上好啊', '晚上好呀', 'good evening'
))
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


@sv.on_fullmatch((
    '晚安', '晚安哦', '晚安啦', 'good night', '晚安呀', '睡咯', '睡啦', '大家晚安'
))
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


@sv.on_keyword((('打你', '打死', '傻')), only_to_me=True)
async def hit_someone(bot, ctx):
    await bot.send(ctx, '我的柴刀呢?', at_sender=True)


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

# ============================================ #


@sv.on_prefix(('戳', '戳一戳'))
async def send_poke(bot, ev):
    user_id = extract_target_members(ev.message)
    text = extract_plain_text(ev.message)
    m = re.match(r'[x|X](\d+)', text)
    if user_id and user_id != 'all':
        if not m:
            for uid in user_id:
                await bot.send(ev, MessageSegment(type_='poke', data={'qq': uid}))
        elif m and int(m.group(1)) <= 5:
            uid = user_id[0]
            for _ in range(int(m.group(1))):
                await bot.send(ev, MessageSegment(type_='poke', data={'qq': uid}))
        else:
            await bot.send(ev, '好累的样子, 我不!')

# ============================================ #


@sv.on_notice('notify.poke')
async def get_poke(session: NoticeSession):
    ev = session.event
    logger.info(f'被{ev.user_id}戳了')
    if ev.self_id == ev['target_id']:
        uid = ev.user_id
        await session.send(MessageSegment(type_='poke', data={'qq': str(uid)}))


@sv.on_notice('group_recall')
async def antiwithdraw(session):
    ev = session.event
    if ev['operator_id'] != ev['self_id']:
        await session.send(
            f'{MessageSegment.at(ev["user_id"])} '
            f'怀孕了就说出来, 大家一起帮你想办法嘛{MessageSegment.face(id_=22)}'
        )


@sv.on_notice('notify')
async def dragon_king(session: NoticeSession):
    ev = session.event
    if ev['sub_type'] == 'honor' and ev['honor_type'] == 'talkative':
        await session.send(f'新的龙王出现了! {MessageSegment.at(ev.user_id)}')


# ============================================ #


@sv.scheduled_job('cron', hour=23)
async def group_good_night():
    bot = get_bot()
    for gid in SUBSCRIBER_GROUP:
        await bot.send_group_msg(group_id=gid, message='晚上十一点, 该准备睡觉了哦~')


@sv.scheduled_job('cron', hour=8)
async def good_morning_group():
    bot = get_bot()
    for gid in SUBSCRIBER_GROUP:
        await bot.send_group_msg(group_id=gid, message='早哦! 新的一天开始了呢!')


@sv.scheduled_job('cron', hour=17)
async def fill_in_the_daily_report():
    bot = get_bot()
    for uid in SUBSCRIBER:
        await bot.send_private_msg(user_id=uid, message='记得填写日报哦')


@sv.scheduled_job('cron', hour=18)
async def remind_to_leave_work():
    bot = get_bot()
    for uid in SUBSCRIBER:
        await bot.send_private_msg(user_id=uid, message='下班了哦, 工作辛苦啦~')

# ===================test===================== #


@sv.on_fullmatch('test_send_mp3')
async def test_send_mp3(bot, ev):
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


@sv.on_fullmatch('test_del_msg')
async def test_del_msg(bot, ev):
    msg = await bot.send(ev, '测试消息')
    import asyncio
    await asyncio.sleep(3)
    await util.delete_msg(ev, msg['message_id'])


@sv.on_fullmatch('test_reply_msg')
async def test_reply_msg(bot, ev):
    reply = MessageSegment(type_='reply', data={'id': ev.message_id})
    await bot.send(ev, f'{reply}做什么呀?')
