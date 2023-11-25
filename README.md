# Alist Sdk

Alist API 简单封装

## [Alist API 文档](https://alist.nn.ci/zh/guide/api/)

## 安装

`pip install alist-sdk`

## 使用

```python
# Sync 模式
from alist_sdk import Client
client = Client(
    base_url='http://localhost:5244',
    username="",
    password="",
    token="", # 与 Username Password 二选一
)

client.me()
client.mkdir("/local/test")
```

```python
# Async 模式
import asyncio
from alist_sdk import AsyncClient

client = AsyncClient(
    base_url='http://localhost:5244',
    username="",
    password="",
    token="",  # 与 Username Password 二选一
)

asyncio.run(client.me())
```
