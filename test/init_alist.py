#!/bin/env python3
"""初始化测试环境"""

import sys
import time
import subprocess
from pathlib import Path

sys.path.append('..')
sys.path.append('.')
from alist_sdk import Client

WORKDIR = Path(__file__).parent
ALIST_EXE = WORKDIR.joinpath("alist/alist") if sys.platform != 'win32' else WORKDIR.joinpath("alist/alist.exe")
if not ALIST_EXE.exists():
    assert subprocess.run(["bash", '-c', f"""
                    mkdir -p {WORKDIR}/alist
                    cd {WORKDIR}/alist
                    wget https://github.com/alist-org/alist/releases/download/v3.28.0/alist-linux-amd64.tar.gz
                    tar xzvf alist-linux-amd64.tar.gz
                    ./alist admin set 123456
                    """]).returncode == 0, "安装alist失败"

assert subprocess.run([str(ALIST_EXE), 'start'], cwd=ALIST_EXE.parent).returncode == 0, "Alist 启动失败"
time.sleep(5)
client = Client("http://localhost:5244", username='admin', password='123456')

test_dir = WORKDIR.joinpath("alist/test_dir")
test_dir.mkdir(parents=True, exist_ok=True)
local_storage = {
    "id": 0,
    "mount_path": "/local",
    "order": 0,
    "driver": "Local",
    "cache_expiration": 0,
    "status": "work",
    "addition": "{\"root_folder_path\":\"%s\",\"thumbnail\":false,\"thumb_cache_folder\":\"\",\"show_hidden\":true,\"mkdir_perm\":\"750\"}" % test_dir.absolute().as_posix(),
    "remark": "",
    "modified": "2023-11-20T15:00:31.608106706Z",
    "disabled": False,
    "enable_sign": False,
    "order_by": "name",
    "order_direction": "asc",
    "extract_folder": "front",
    "web_proxy": False,
    "webdav_policy": "native_proxy",
    "down_proxy_url": ""
}

if '/local' not in [i['mount_path'] for i in client.get("/api/admin/storage/list").json()['data']['content']]:
    assert client.post(
        "/api/admin/storage/create",
        json=local_storage
    ).json().get('code') == 200, "创建Storage失败。"
else:
    print("已经创建，跳过 ...")
