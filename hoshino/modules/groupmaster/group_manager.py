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
          "[开除@成员]将成员开除出群"
)


@sv.on_prefix('申请头衔')
async def to_apply_for_title(bot, ev):
    special_title = []
    for msg_seg in ev.message:
        if msg_seg.type == 'text' and msg_seg.data['text']:
            special_title.append(msg_seg.data['text'].strip())
    if not special_title:
        await bot.send(ev, '你想要什么头衔呀?', at_sender=True)
    else:
        special_title = ''.join(special_title)
        await util.set_group_special_title(ev, special_title=special_title)


@sv.on_prefix(['kick', '踢出', '踢了', '开除', '欢送'])
async def kick(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我才不会听你的命令呢! 哼~', at_sender=True)
        return
    user_id = None
    for msg_seg in ev.message:
        if msg_seg.type == 'at':
            if msg_seg.data['qq'] == 'all':
                await bot.send(ev, '诶? 你要把大家都赶走吗? 不可以哦~')
                return
            else:
                user_id = int(msg_seg.data['qq'])
    if user_id:
        await bot.send(ev, f'{MessageSegment.at(user_id)} 再~见~啦~')
        await asyncio.sleep(3)
        if user_id in config.SUPERUSERS:
            await bot.send(ev, '开玩笑的~我才不会对主人下手呢!')
            return
        await util.kick(ev, user_id=user_id)
    else:
        await bot.send(ev, '你要把谁送走呀?', at_sender=True)


@sv.on_prefix(['授予头衔'])
async def awarded_title(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有管理员可以颁发头衔哟~')
        return
    user_id = None
    special_title = []
    for msg_seg in ev.message:
        if msg_seg.type == 'text' and msg_seg.data['text'].strip():
            special_title.append(msg_seg.data['text'].strip())
        if msg_seg.type == 'at':
            if msg_seg.data['qq'] == 'all':
                await bot.send(ev, '诶~? 你是想累死我吗!?')
                return
            else:
                user_id = int(msg_seg.data['qq'])
    if user_id is None:
        await bot.send(ev, '这个头衔, 你是打算给谁?')
        return
    if not special_title:
        await bot.send(ev, '这是要发皇帝的新头衔吗? 我不会呀T^T')
        return
    else:
        special_title = ''.join(special_title)
        await util.set_group_special_title(
            ev, special_title=special_title, user_id=user_id)


@sv.on_suffix(['禁言', '塞口球', '闭嘴', '住口'])
async def mute(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我才不会听你的命令呢! 哼~', at_sender=True)
        return
    user_id = None
    for msg_seg in ev.message:
        if msg_seg.type == 'at':
            if msg_seg.data['qq'] == 'all':
                await bot.send(ev, '全员禁言吗? 我还在学呢~')
                return
            else:
                user_id = int(msg_seg.data['qq'])
    if user_id:
        # await asyncio.sleep(3)
        if user_id in config.SUPERUSERS:
            await bot.send(ev, '我才不会对主人下手呢!')
            return
        await util.members_banned(ev, user_id, 60*5)
        await bot.send(ev, f'{MessageSegment.at(user_id)} 请你安静一点啦~')
    else:
        await bot.send(ev, '你要禁言谁呀?', at_sender=True)


@sv.on_prefix('解除禁言')
async def remove_banned(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我只听主人的话哦~', at_sender=True)
        return
    user_id = None
    for msg_seg in ev.message:
        if msg_seg.type == 'at':
            if msg_seg.data['qq'] == 'all':
                await bot.send(ev, '人家还不会啦, 你自己动手嘛~')
                return
            else:
                user_id = int(msg_seg.data['qq'])
    if user_id:
        # await asyncio.sleep(3)
        await util.members_banned(ev, user_id, 0)
        await bot.send(ev, f'{MessageSegment.at(user_id)} 你可以说话咯~')
    else:
        await bot.send(ev, '你要解除谁的禁言呀?', at_sender=True)


@sv.on_prefix(['设置管理', '设置管理员', '举荐'])
async def set_up_an_administrator(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我才不会听你的命令呢! 哼~', at_sender=True)
        return
    user_id = None
    for msg_seg in ev.message:
        if msg_seg.type == 'at':
            if msg_seg.data['qq'] == 'all':
                # await bot.send(ev, '诶? 你要把大家都赶走吗? 不可以哦~')
                return
            else:
                user_id = int(msg_seg.data['qq'])
    if user_id:
        await bot.send(ev, f'{MessageSegment.at(user_id)} 恭喜升职~加薪~走向人生巅峰!')
        await util.set_up_an_administrator(ev, user_id=user_id, enable=True)
    else:
        await bot.send(ev, '喵？')


@sv.on_prefix(['取消管理', '取消管理员', '罢免'])
async def cancel_administrator(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '我才不会听你的命令呢! 哼~', at_sender=True)
        return
    user_id = None
    for msg_seg in ev.message:
        if msg_seg.type == 'at':
            if msg_seg.data['qq'] == 'all':
                # await bot.send(ev, '诶? 你要把大家都赶走吗? 不可以哦~')
                return
            else:
                user_id = int(msg_seg.data['qq'])
    if user_id:
        await util.set_up_an_administrator(ev, user_id=user_id, enable=False)
    else:
        await bot.send(ev, '喵？')
