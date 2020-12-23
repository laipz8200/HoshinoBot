from hoshino import Service, get_bot

sv = Service(
    'anti-msg-recall',
    enable_on_default=False,
    visible=True,
    help_="反撤回功能"
)


@sv.on_notice('group_recall')
async def antiwithdraw(session):
    ev = session.event
    gid = ev['group_id']
    mid = ev['message_id']
    uid = ev['user_id']
    oid = ev['operator_id']
    msg = await get_bot().get_msg(message_id=mid)
    user = await get_bot().get_group_member_info(group_id=gid, user_id=uid)
    if oid == uid and uid != ev['self_id']:
        await session.send(
            f'{user["card"]}({uid})撤回的消息是:\n{msg["message_raw"]}'
        )
