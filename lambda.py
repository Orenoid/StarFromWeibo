import json
import os
import re
from http.cookies import SimpleCookie

import requests

print('Loading function')

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
FORWARD_KEY = os.environ.get('FORWARD_KEY')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def parse_text_to_repo_name(body: str, forward_key: str) -> (str, str):
    url = 'https://openai.api2d.net/v1/chat/completions'
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {"role": "system", "content": "尝试从用户发送给你的文本里找出GitHub Repo名字，并以{owner}/{repo}的形式回复用户，"
                                          "若文本与GitHub无关，则回复null，绝对不要返回多余内容"},
            {"role": 'user', 'content': body}
        ]
    }
    resp = requests.post(url, headers={'Authorization': f'Bearer {forward_key}'}, json=payload)
    print(resp.text)
    resp.raise_for_status()
    content = resp.json()['choices'][0]['message']['content']
    if content == 'null':
        return '', ''
    splits = content.split('/')
    if len(splits) == 2:
        return splits[0], splits[1]
    pattern = r"(https?://)?github\.com/([\w-]+)/([\w-]+)"
    match = re.match(pattern, content)
    if match:
        return match.group(2), match.group(3)
    else:
        raise Exception(f'invalid content: {content}')


def star(owner: str, repo: str, token: str):
    url = f'https://api.github.com/user/starred/{owner}/{repo}'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    resp = requests.put(url, headers=headers)
    print(resp.text)
    resp.raise_for_status()


def get_long_text(mblogid: str, cookie: str) -> str:
    url = "https://weibo.com/ajax/statuses/longtext"
    params = {'id': mblogid}
    headers = {
        'authority': 'weibo.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5',
        'client-version': 'v2.40.37',
        'cookie': cookie,
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

    resp = requests.request("GET", url, headers=headers, params=params)
    resp.raise_for_status()
    resp_json = resp.json()
    return resp_json['data']['longTextContent']


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    request_raw: str = event['body']
    request_json: dict = json.loads(request_raw)
    value_raw = request_json.get('value')
    print(value_raw)
    value_json: dict = json.loads(value_raw)

    message: str = 'no repo to star'
    if value_raw is not None:
        text_raw = value_json.get('text_raw')
        if value_json.get('isLongText'):
            mblogid = value_json.get('mblogid')
            text_raw = get_long_text(mblogid, value_json.get('cookie'))

        owner, repo = parse_text_to_repo_name(text_raw, FORWARD_KEY)
        if owner != '' and repo != '':
            star(owner, repo, GITHUB_TOKEN)
            message = f'starred repo: {owner}/{repo}'
            destroy_fav(value_json.get('id'), value_json.get('cookie'))

    print(message)
    payload = {
        'code': 200,
        'message': message
    }
    return respond(None, payload)


def destroy_fav(wb_id: int, cookie: str):
    url = "https://weibo.com/ajax/statuses/destoryFavorites"

    simple_cookie = SimpleCookie()
    simple_cookie.load(cookie)
    xsrf_token = simple_cookie['XSRF-TOKEN'].value

    payload = {'id': str(wb_id)}
    headers = {
        'authority': 'weibo.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': cookie,
        'dnt': '1',
        'origin': 'https://weibo.com',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': xsrf_token,
    }

    resp = requests.request("POST", url, headers=headers, json=payload)
    print(resp.text)
    resp.raise_for_status()
