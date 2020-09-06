# HoshinoBot

A qqbot for Princess Connect Re:Dive (and other usage :)

## 简介

**HoshinoBot:** 基于 [nonebot](http://nonebot.cqp.moe) 框架，开源、无公害、非转基因的QQ机器人。

本项目为改造版，如需使用请查看[Ice-Cirno/HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)。

## 已添加功能

### 群组管理

- 将指定成员踢出群聊
- 成员申请头衔
- 管理指定授予头衔
- 对某成员执行5分钟禁言
- 解除某成员的禁言

### 点歌

- 返回QQ音乐和网易云搜索结果各3首
- 从结果中选择歌曲

> go-cqhttp分享QQ音乐时会丢失标题，建议使用cqhttp-mirai获得更好的体验。
> 当前请求为同步方法，非最终版本。

**点歌所需依赖**

```shell
pycryptodomex
httpx
```
