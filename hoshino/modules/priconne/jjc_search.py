import pandas as pd
from hoshino import Service, aiorequests, priv, util
from lxml import etree

sv = Service('jjc_query', manage_priv=priv.ADMIN,
             enable_on_default=False, bundle='pcr查询')


async def search(user_id):
    data = {'user_id': user_id}
    headers = {
        'Host': 'jjc-finder.wa.vg',
        'Connection': 'keep-alive',
        'Origin': 'http://jjc-finder.wa.vg',
        'Content - Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                  'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://jjc-finder.wa.vg/',
        'Accept-Encoding': 'none',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        resp = await aiorequests.post('http://jjc-finder.wa.vg/', headers=headers, data=data)
        return await resp.text
    except:
        return "error"


@sv.on_prefix(('/jjc', 'jjc场次'))
async def get_jjc(bot, ev):
    user_id = str(ev.message.extract_plain_text())
    if not user_id.isdigit():
        await bot.send(ev, '请在这个指令后加上 13 位 id 哦~')
        return
    if len(user_id) != 13:
        await bot.send(ev, 'ん ?')
        return
    req = await search(user_id)
    if req == "error":
        await bot.send(ev, '出现意外情况, 请重新尝试, 或与维护组联系。')
        return
    pretreatment = etree.HTML(req)
    table = pretreatment.xpath('/html/body/div/div[2]/table')
    table = etree.tostring(table[0], encoding='utf-8').decode()
    df = pd.read_html(table, encoding='utf-8', header=0)[0]
    results = list(df.T.to_dict().values())
    name = results[0][user_id]
    lv_exp = results[1][user_id]
    power = results[2][user_id]
    jjc = results[3][user_id]
    pjjc = results[4][user_id]
    reply = f"""你正在查询id为{user_id}的用户\n用户名 {name}\n等级/经验 {lv_exp}\n战力有 {power}\njjc 被分到了 {jjc}\npjjc 被分到了 {pjjc}"""
    await bot.send(ev, reply, at_sender=False)
    await util.silence(ev, 120, user_id=ev['user_id'])
