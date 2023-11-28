import json
import logging
from pathlib import Path

from .models import Resp
from .client import Client

logger = logging.getLogger('alist-sdk.tools')


def printf(key, data, res: Resp):
    """记录"""
    name = '' if isinstance(data, list) else (
            data.get("mount_path") or data.get('path') or data.get('username')
    )
    if res.code == 200:
        print(f"created {key} [{name}]")
    else:
        print(f'Error: {key} [{name}]: {res.code}: {res.message}')


def input_config_from_json(client: Client, config_file: str):
    """从JSON中导入配置"""
    configs: dict = json.loads(Path(config_file).read_text())

    apis = {
        'settings': '/api/admin/setting/save',
        'users': '/api/admin/user/create',
        'storages': '/api/admin/storage/create',
        'metas': '/api/admin/meta/create',
    }

    for k, vs in configs.items():
        if k == 'settings':
            res = client.verify_request(
                'POST',
                apis[k],
                json=vs
            )
            printf(k, vs, res)
            continue
        else:
            for v in vs:
                res = client.verify_request(
                    "POST",
                    apis[k],
                    json=v
                )
                printf(k, v, res)
