import asyncio

from aiocqhttp.message import MessageSegment

from hoshino import Service, config, priv, util

sv = Service(
    'group-manager',
    enable_on_default=False,
    visible=True,
    help_="群管理功能，bot作为群主时有效\n"
          "[申请头衔XXX]向群主申请一个头衔\n"
          "[授予头衔XXX@成员]发放头衔给成员\n"
          "[开除@成员]将成员开除出群\n"
          "[@成员 禁言]将成员禁言五分钟\n"
          "[解除禁言@成员]解除成员的禁言\n"
          "[戳一戳@成员]戳一戳"
)


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


@sv.on_prefix('申请头衔')
async def to_apply_for_title(bot, ev):
    special_title = extract_plain_text(ev.message)
    if not special_title:
        await bot.send(ev, '你想要什么头衔呀?', at_sender=True)
    else:
        await util.set_group_special_title(ev, special_title=special_title)


@sv.on_prefix(('kick', '踢出', '踢了', '开除', '欢送'))
async def kick(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我才不会听你的命令呢! 哼~', at_sender=True)
        return
    user_id = extract_target_members(ev.message)
    if not user_id:
        await bot.send(ev, '你要把谁送走呀?', at_sender=True)
        return
    elif user_id == 'all':
        await bot.send(ev, '诶? 你要把大家都赶走吗? 不可以哦~')
        return
    else:
        user_id = list(map(lambda u: int(u), user_id))
    await bot.send(ev, ''.join([f'{MessageSegment.at(u_id)}' for u_id in user_id]) + ' 再~见~啦~')
    await asyncio.sleep(5)
    for uid in user_id:
        if uid in config.SUPERUSERS:
            # await bot.send(ev, '开玩笑的~我才不会对主人下手呢!')
            continue
        else:
            await util.kick(ev, user_id=uid)


@sv.on_prefix(('授予头衔', '颁发头衔', '发布头衔', '给予头衔'))
async def awarded_title(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有管理员可以颁发头衔哟~')
        return
    user_id = extract_target_members(ev.message)
    special_title = extract_plain_text(ev.message)
    if not user_id:
        await bot.send(ev, '这个头衔, 你是打算给谁?')
        return
    elif user_id == 'all':
        await bot.send(ev, '诶~? 你是想累死我吗!?')
        return
    else:
        user_id = int(user_id[0])
    if not special_title:
        await bot.send(ev, '这是要发皇帝的新头衔吗? 我不会呀T^T')
        return
    else:
        await util.set_group_special_title(ev, special_title=special_title, user_id=user_id)


@sv.on_suffix(('禁言', '塞口球', '闭嘴', '住口'))
async def mute(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我才不会听你的命令呢! 哼~', at_sender=True)
        return
    user_id = extract_target_members(ev.message)
    if not user_id:
        await bot.send(ev, '你要禁言谁呀?', at_sender=True)
        return
    elif user_id == 'all':
        await bot.send(ev, '全员禁言吗? 我还在学呢~')
        return
    else:
        user_id = list(map(lambda u: int(u), user_id))
    await bot.send(ev, ''.join([f'{MessageSegment.at(uid)}' for uid in user_id]) + ' 请安静一会儿啦~')
    for uid in user_id:
        if uid in config.SUPERUSERS and len(user_id) > 1:
            # await bot.send(ev, '我才不会对主人下手呢!')
            continue
        else:
            await util.members_banned(ev, uid, 60*5)


@sv.on_prefix('解除禁言')
async def remove_banned(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我只听主人的话哦~', at_sender=True)
        return
    user_id = extract_target_members(ev.message)
    if not user_id:
        await bot.send(ev, '你要解除谁的禁言呀?', at_sender=True)
        return
    if user_id == 'all':
        await bot.send(ev, '人家还不会啦, 你自己动手嘛~')
        return
    else:
        user_id = list(map(lambda u: int(u), user_id))
    for uid in user_id:
        await util.members_banned(ev, uid, 0)
    await bot.send(ev, ''.join([f'{MessageSegment.at(uid)}' for uid in user_id]) + ' 出来放风咯~')


@sv.on_prefix(('戳', '戳一戳'))
async def stamp(bot, ev):
    user_id = extract_target_members(ev.message)
    if user_id and user_id != 'all':
        for uid in user_id:
            await bot.send(ev, MessageSegment(type_='poke', data={'qq': uid}))
