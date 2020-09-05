import typing

from aiocqhttp.message import MessageSegment

from hoshino import Service, logger

from .search_netease_cloud_music import search as search163
from .search_qq_music import search as searchqq

sv = Service(
    'music',
    enable_on_default=True,
    visible=True,
    help_=""
)


@sv.on_prefix('点歌')
async def to_apply_for_title(bot, ev):
    music_name = []
    for msg_seg in ev.message:
        if msg_seg.type == 'text' and msg_seg.data['text']:
            music_name.append(msg_seg.data['text'].strip())
    if not music_name:
        await bot.send(ev, '你想听什么呀?', at_sender=True)
    else:
        music_name = ''.join(music_name)
        songs, _id, _type = search_netease_cloud_music(music_name)
        if songs:
            _music = MessageSegment.music(type_=_type, id_=_id)
            logger.info(f'点歌{music_name}成功')
            await bot.send(ev, _music)
        else:
            await bot.send(ev, '什么也没有找到的说OxO')


def search_netease_cloud_music(music_name: str) -> typing.Union[list, dict]:
    data = search163(music_name)['songs']
    if data and data[0]['name'] == music_name:
        return data[0]['name'], data[0]['id'], '163'
    data = searchqq(music_name)
    if data:
        return data[0]['songname'], data[0]['songid'], 'qq'
    return None, None, None
