# coding: utf-8
# powered by [Chendihe](https://github.com/Chendihe4975)
import datetime

import psutil
from hoshino import Service, priv

sv = Service(
    'bot-status', manage_priv=priv.ADMIN,
    enable_on_default=True, visible=False
)


@sv.on_fullmatch('/info')
async def push_info(bot, ev):
    a = psutil.cpu_count(logical=False)
    b = psutil.cpu_count()
    c = psutil.cpu_percent()
    d = psutil.virtual_memory().percent
    e = psutil.disk_usage('/').percent
    f = datetime.datetime.fromtimestamp(
        psutil.boot_time()).strftime("%Y-%m-%d %H: %M: %S")
    msg = f'当前服务器状态: \nCPU物理个数: {a} 个\nCPU逻辑个数: {b} 个\nCPU使用率: {c}%\n内存使用率: {d}%\n磁盘使用百分比: {e}%\n开机时间: {f}'
    await bot.send(ev, msg, at_sender=False)


@sv.on_fullmatch('/netinfo')
async def speed_test(bot, ev):
    net_io_send = round(psutil.net_io_counters().bytes_sent/1024/1024, 2)
    net_io_recv = round(psutil.net_io_counters().bytes_recv/1024/1024, 2)
    net_packets_sent = psutil.net_io_counters().packets_sent
    net_packets_recv = psutil.net_io_counters().packets_recv
    net_packet_lost = round(
        psutil.net_io_counters().packets_recv / psutil.net_io_counters().packets_sent, 2
    )
    msg = f'当前服务器网络状态: \n发送: {net_io_send} MB\n接收: {net_io_recv} MB\n发包: {net_packets_sent}个\n回复: {net_packets_recv} 个\n丢包率: {net_packet_lost} %'
    await bot.send(ev, msg)
