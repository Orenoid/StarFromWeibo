import json
import os

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
    return content.split('/')


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


def get_long_text(id: str) -> str:
    url = 'https://weibo.com/ajax/statuses/longtext'
    params = {'id': id}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()['data']


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    request_raw: str = event['body']
    request_json: dict = json.loads(request_raw)
    value_raw = request_json.get('value')
    # value_json: dict = json.loads(value_raw)

    # if value_json.get('isLongText'):
    #     mblogid = value_json.get('mblogid')
    #     todo 获取需要展开的长文微博内容

    message: str = 'no repo to star'
    if value_raw is not None:
        owner, repo = parse_text_to_repo_name(value_raw, FORWARD_KEY)
        if owner != '' and repo != '':
            star(owner, repo, GITHUB_TOKEN)
            message = f'starred repo: {owner}/{repo}'

    print(message)
    payload = {
        'code': 200,
        'message': message
    }
    return respond(None, payload)
