# StarFromWeibo

Weibo -> CheckChan -> AWS Lambda + ChatGPT -> GitHub API

定时爬取收藏的微博，解析与 GitHub 有关的部分，自动将微博里提到的 Repo 同步到 GitHub Stars 中

## TODO
- lambda 接口鉴权
- 错误处理
- gpt temperature params