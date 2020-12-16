from aiocqhttp.message import MessageSegment
from hoshino import Service, logger, priv
from hoshino.typing import CQEvent

from .dao.dbnamesqlitedao import TLDBNameDao
from .dao.timelinesqlitedao import TLSqliteDao

sv = Service('timeline', bundle='pcr会战', enable_on_default=False, help_='''
传轴 <A|B><1-5> <伤害> <说明> <轴>
查轴 [A|B][1-5]
看轴 [编号]
改轴 <编号> <伤害> <说明> <轴>
删轴 <编号>
赞轴 <编号> [赞同数,非管理员只能填1|-1]
查看轴库
切换轴库 <新轴库名>
'''.strip())


recent = {}


def tid2id(tid):
    try:
        return int(tid.strip('T'))
    except:
        return -1


def get_dbname(group_id):
    db = TLDBNameDao(group_id)
    return db._find_by_id(group_id)


@sv.on_prefix(('查看轴库名', '查询轴库名', '查看轴库'))
async def search_dbname(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '抱歉，您无权使用此指令，请联系管理员')
        return
    else:
        db = TLDBNameDao(ev.group_id)
        await bot.send(ev, '当前轴库名为: ' + db._find_by_id(ev.group_id))


@sv.on_prefix(('修改轴库名', '改变轴库', '变更轴库', '设定轴库', '切换轴库'))
async def modify_dbname(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '抱歉，您无权使用此指令，请联系管理员')
        return
    else:
        s = ev.message.extract_plain_text()
        if s == '':
            await bot.send(ev, '修改轴库名失败，名称不能为空')
        else:
            db = TLDBNameDao(ev.group_id)
            db._update_by_id(ev.group_id, ev.message.extract_plain_text())
            await bot.send(ev, '修改轴库名成功')


@sv.on_prefix(('赞轴', '赞同轴'))
async def approve_timeline(bot, ev: CQEvent):
    try:
        s = ev.message.extract_plain_text().rstrip().split(' ', 2)
        if not priv.check_priv(ev, priv.ADMIN) and len(s) == 2 and abs(int(s[1])) != 1:
            await bot.send(ev, '赞同失败，非管理员单次赞同数只能为1或-1')
            return
        approval = 1 if len(s) == 1 else int(s[1])
        db = TLSqliteDao(get_dbname(ev.group_id))
        db._add_approval(tid2id(s[0]), approval)
        await bot.send(ev, '感谢您的反馈!')
    except:
        await bot.send(ev, '赞同失败，请输入\"帮助pcr轴\"查看指令的使用方式')


@sv.on_prefix(('录入轴', '上传轴', '添加轴', '传轴'))
async def insert_timeline(bot, ev: CQEvent):
    try:
        msg = ev.message
        s = ''
        for seg in msg:
            s += ' ' + str(seg).strip()
        s = s.lstrip().split(' ', 3)
        db = TLSqliteDao(get_dbname(ev.group_id))
        db._insert(s[0], s[1], s[2], s[3].strip(), ev.user_id)
        await bot.send(ev, '录入完毕!')
    except:
        await bot.send(ev, '录入轴失败，请输入\"帮助pcr会战\"查看指令的使用方式')


@sv.on_prefix(('查找轴', '查看轴', '查轴', '看轴'))
async def search_timeline(bot, ev: CQEvent):
    gid = str(ev.group_id)
    if gid not in recent:
        recent[gid] = []
    if len(recent[gid]) > 4:
        recent[gid] = recent[gid][-4:]
    try:
        s = ev.message.extract_plain_text()
        if s in recent[gid]:
            await bot.send(ev, '这个轴才发过不久, 往上翻一翻吧~', at_sender=True)
            return
        db = TLSqliteDao(get_dbname(ev.group_id))
        if len(s) == 0:
            await bot.send(ev, '为防止长消息风控, 请输入具体的BOSS编号, 如B1', at_sender=True)
        elif s.startswith('T'):
            recent[gid].append(s)
            r = db._find_by_id(tid2id(s))
            msg = f'{r[0]}, {r[1]}伤害, {r[3]}\n'
            await bot.send(ev, msg + r[2])
        else:
            recent[gid].append(s)
            r = db._find_by_bossname(s)
            msg = [
                f'{MessageSegment.at(user_id=ev.user_id)}\n编号|boss|伤害|备注|赞同数']
            msg.extend(r)
            await bot.send(ev, '\n'.join(msg))
    except Exception as e:
        logger.error(e)
        await bot.send(ev, '查找轴失败，请输入\"帮助pcr会战\"查看指令的使用方式')


@sv.on_prefix(('修改轴', '更新轴', '改轴'))
async def update_timeline(bot, ev: CQEvent):
    try:
        msg = ev.message
        s = ''
        for seg in msg:
            s += ' ' + str(seg).strip()
        s = s.lstrip().split(' ', 3)
        db = TLSqliteDao(get_dbname(ev.group_id))
        userid = 999 if priv.check_priv(ev, priv.ADMIN) else ev.user_id
        if db._update_by_id(tid2id(s[0]), s[1], s[2], s[3].strip(), userid):
            await bot.send(ev, f'修改轴{s[0]}成功')
        else:
            await bot.send(ev, '您非该轴的上传者或管理员，无修改权限')
    except:
        await bot.send(ev, '修改轴失败，请输入\"帮助pcr会战\"查看指令的使用方式')


@sv.on_prefix(('删轴', '删除轴'))
async def delete_timeline(bot, ev: CQEvent):
    try:
        s = ev.message.extract_plain_text()
        db = TLSqliteDao(get_dbname(ev.group_id))
        userid = 999 if priv.check_priv(ev, priv.ADMIN) else ev.user_id
        if db._del_by_id(tid2id(s), userid):
            await bot.send(ev, f'删除轴{s}成功')
        else:
            await bot.send(ev, '您非该轴的上传者或管理员，无删除权限')
    except:
        await bot.send(ev, '删除轴失败，请输入\"帮助pcr会战\"查看指令的使用方式')
