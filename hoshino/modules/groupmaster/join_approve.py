from nonebot import RequestSession, message, on_request

import hoshino


@on_request('group.add')
async def join_approve(session: RequestSession):
    cfg = hoshino.config.groupmaster.join_approve
    gid = session.event.group_id
    if gid not in cfg:
        return
    for k in cfg[gid].get('keywords', []):
        if k in session.event.comment:
            await session.approve()
            for uid in hoshino.config.SUPERUSERS:
                await hoshino.get_bot().send_private_msg(user_id=uid, message=f'群{gid}新成员{session.event["user_id"]}的入群口令为{k}')
            # 审批入群后发送欢迎信息
            welcomes = hoshino.config.groupmaster.increase_welcome
            if gid in welcomes:
                await session.send(welcomes[gid], at_sender=True)
            return
    if cfg[gid].get('reject_when_not_match', False):
        await session.reject()
        return
