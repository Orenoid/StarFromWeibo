import http.client
import json
import os

WEIBO_UID = 42  # 把自己收藏页 URL 里面的 UID 填到这里

conn = http.client.HTTPSConnection("weibo.com")
payload = ''
headers = {
    'authority': 'weibo.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5',
    'client-version': 'v2.40.37',
    'cookie': os.environ.get('COOKIE'),
    'dnt': '1',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'server-version': 'v2023.04.21.1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}
conn.request("GET", f"/ajax/favorites/all_fav?uid={WEIBO_UID}&page=1", payload, headers)
res = conn.getresponse()
data = res.read()

data_json: dict = json.loads(data.decode("utf-8"))
first_post: dict = data_json['data'][0]
result = {
    'text_raw': first_post['text_raw'],
    'isLongText': first_post['isLongText'],
    'mblogid': first_post['mblogid'],
    'id': first_post['id'],
    'cookie': os.environ.get('COOKIE')
}

print(json.dumps(result, ensure_ascii=False))
