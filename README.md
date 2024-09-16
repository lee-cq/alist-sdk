# Alist Sdk

[![Alist SDK - Test](https://github.com/lee-cq/alist-sdk/actions/workflows/CI.yaml/badge.svg)](https://github.com/lee-cq/alist-sdk/actions/workflows/CI.yaml)

Alist API 简单封装

## [Alist API 文档](https://alist.nn.ci/zh/guide/api/)

## 安装

从PyPI安装最新release版本  
`pip install alist-sdk`

从GitHub安装dev版本  
`pip install git+https://github.com/lee-cq/alist-sdk.git`

## 使用

客户端或异步客户端方法签名于API基本一致。

```python
# Sync 模式
from alist_sdk import Client

client = Client(
    base_url='http://localhost:5244',
    username="",
    password="",
    token="",  # 与 Username Password 二选一
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

像使用pathlib一样操作Alist上的文件。
但是需要注意的是，AlistPath全部使用的同步方法（与Pathlib API保持一致）。
如果需要异步操作，可以使用`asyncio.to_thread`将同步方法转为异步方法。

```python
from alist_sdk.path_lib import login_server, AlistPath

# 登录方式1
login_server("http://localhost:5244", username='admin', password='123456')
path = AlistPath('http://localhost:5244/test')

# 登录方式2 version > 0.36.13
path = AlistPath('http://localhost:5244/test', username='admin', password='123456')

path.stat()
path.is_dir()
path.read_text()
path.iterdir()
```

## 命令行工具 [开发中]

Alist SDK 提供了2个命令行工具，可以方便的操作Alist。

1. `alist-cli`：命令行工具，可以快速的操作Alist。
2. `alist-fs`：(`alist-cli fs` 的别名)文件相关操作，包括上传、下载、删除、查看文件信息等。

```
Usage: alist-cli [OPTIONS] COMMAND [ARGS]...
Options:
│ --install-completion          Install completion for the current shell.                                                                                                                                                            │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                                                                                     │
│ --help   
    
Commands:
│ admin   管理命令                                                                                                                                                                                                                   │
│ auth    Authentication commands.                                                                                                                                                                                                   │
│ fs      文件系统相关操作  
```