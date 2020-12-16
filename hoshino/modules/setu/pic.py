import os
import random
from datetime import datetime
from hashlib import md5
from pathlib import Path

from hoshino import R, Service, aiorequests, priv, util
from nonebot.exceptions import CQHttpError

sv = Service('pic', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=True)
setu_folder = R.img('pic/').path


async def get_new_setu(num: int = 1):
    for _ in range(num):
        resp = await aiorequests.get('https://呐.art/p.jpg')
        # resp = await aiorequests.get('https://michikawachin.art')
        if resp.status_code == 200:
            content = await resp.content
            m = md5()
            m.update(content)
            file_name = Path(setu_folder) / Path(f'{m.hexdigest()}.png')
            with file_name.open('wb') as f:
                f.write(content)
            sv.logger.info(f'已下载{file_name}')
        else:
            sv.logger.info('下载失败')


@sv.scheduled_job('cron', minute='*/5', jitter=20, next_run_time=datetime.now())
async def sonet_news_poller():
    dir = Path(setu_folder)
    file_list = list(dir.iterdir())
    count = len(file_list)
    if count < 20:
        sv.logger.info('开始补充20张图片')
        await get_new_setu(20)
    elif count < 50:
        sv.logger.info('开始补充10张图片')
        await get_new_setu(10)
    elif count < 100:
        sv.logger.info('开始补充1张图片')
        await get_new_setu(1)
    else:
        for file in (new_file_list := file_list[::2]):
            file.unlink()
        sv.logger.info(f'删除{len(new_file_list)}张图片')


def setu_gener():
    while True:
        filelist = os.listdir(setu_folder)
        random.shuffle(filelist)
        for filename in filelist:
            if os.path.isfile(os.path.join(setu_folder, filename)):
                yield R.img('pic/', filename)


setu_gener = setu_gener()


def get_setu():
    return setu_gener.__next__()


@sv.on_rex(r'不够[瑟色涩]|来一?[点份张].*[涩色]图|想看[瑟色涩]图')
async def setu(bot, ev):
    month = datetime.now().month
    await bot.send(ev, f'{month}月不冲！请改用健全的新功能【随机图片】')



@sv.on_fullmatch('随机图片')
async def pic(bot, ev):
    """随机发送一张图库中的图片"""
    uid = ev['user_id']
    pic = get_setu()

    try:
        await bot.send(ev, pic.cqcode)
        await util.silence(ev, 60, user_id=uid)
    except CQHttpError:
        pass
