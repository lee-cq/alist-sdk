#!/bin/env python3
"""初始化测试环境"""
import sys
import time
import subprocess
from pathlib import Path

sys.path.append('..')
from alist_sdk import Client

WORKDIR = Path(__file__).parent.parent
if not WORKDIR.joinpath("/alist/alist").exists():
    assert subprocess.run(["bash", '-c', f"""
                    mkdir -p {WORKDIR}/alist
                    cd {WORKDIR}/alist
                    wget https://github.com/alist-org/alist/releases/download/v3.28.0/alist-linux-amd64.tar.gz
                    tar xzvf alist-linux-amd64.tar.gz
                    ./alist admin set 123456
                    ./alist start
                    """]).returncode == 0, "安装alist失败"

time.sleep(10)
client = Client("http://localhost:5244", username='admin', password='123456')

local_storage = {"id":0,
                 "mount_path":"/local",
                 "order":0,
                 "driver":"Local",
                 "cache_expiration":0,
                 "status":"work",
                 "addition":"{\"root_folder_path\":\"%s\",\"thumbnail\":false,\"thumb_cache_folder\":\"\",\"show_hidden\":true,\"mkdir_perm\":\"750\"}" % Path('.').absolute(),
                 "remark":"",
                 "modified":"2023-11-20T15:00:31.608106706Z",
                 "disabled":False,
                 "enable_sign":False,
                 "order_by":"",
                 "order_direction":"",
                 "extract_folder":"",
                 "web_proxy":False,
                 "webdav_policy":"native_proxy",
                 "down_proxy_url":""
                 }

# if client.post("/api/admin/storage/list").json()['data']
assert client.post("/api/admin/storage/create", json=local_storage).json().get('code') == 200, "创建Storage失败。"