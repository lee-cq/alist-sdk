import json
import logging
from pathlib import Path

from alist_sdk.models import Resp
from alist_sdk.client import Client
from alist_sdk.tools.models import Configs

logger = logging.getLogger('alist-sdk.tools')

__all__ = ["import_configs_from_dict",
           "import_configs_from_json_str",
           "import_configs_from_json_file",
           ]


def __printf(key, data, res: Resp):
    """记录"""
    name = '' if isinstance(data, list) else (
            data.get("mount_path") or data.get('path') or data.get('username')
    )
    if res.code == 200:
        print(f"created {key} [{name}]")
    else:
        print(f'Error: {key} [{name}]: {res.code}: {res.message}')


def import_configs_from_dict(client: Client, configs: dict):
    """从JSON中导入配置"""
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
            __printf(k, vs, res)
            continue
        else:
            for v in vs:
                res = client.verify_request(
                    "POST",
                    apis[k],
                    json=v
                )
                __printf(k, v, res)


def import_configs_from_json_str(client, json_data: str):
    """"""
    return import_configs_from_dict(client, json.loads(json_data))


def import_configs_from_json_file(client, json_file):
    """"""
    if not Path(json_file).exists():
        raise FileNotFoundError()
    return import_configs_from_json_str(client, Path(json_file).read_text())


def export_configs(client: Client) -> Configs:
    """"""
    apis = {
        'settings': '/api/admin/setting/list',
        'users': '/api/admin/user/list',
        'storages': '/api/admin/storage/list',
        'metas': '/api/admin/meta/list',
    }
