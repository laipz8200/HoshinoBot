import httpx

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"


def search(keyword):
    """ 搜索音乐 """
    number = 5
    params = {"w": keyword, "format": "json", "p": 10, "n": number}

    headers = {
        "referer": "http://m.y.qq.com",
        "User-Agent": USER_AGENT
    }
    res_data = httpx.get(
        url="http://c.y.qq.com/soso/fcgi-bin/search_for_qq_cp",
        params=params,
        headers=headers
    ).json()
    data = res_data['data']['song']['list']
    for item in data:
        if item['songname'] == keyword:
            return [item]
    return []


if __name__ == "__main__":
    data = search('Muse')[0]
    print(data['songname'], data['songid'])
