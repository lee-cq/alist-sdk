# Alist Sdk

Alist API 简单封装

## [Alist API 文档](https://alist.nn.ci/zh/guide/api/)

## 安装

`pip install alist-sdk`

## 使用

客户端或异步客户端方法签名于API基本一致。

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

像使用pathlib一样操作Alist上的文件，但是需要注意的是，AlistPath的方法都是同步的，如果需要异步操作，可以使用`asyncio.to_thread`将同步方法转为异步方法。
```python
from alist_sdk.path_lib import login_server, AlistPath

login_server("http://localhost:5244", username='admin', password='123456')

path = AlistPath('http://localhost:5244/test')
path.stat()
path.is_dir()
path.read_text()
path.iterdir()
```