import json
import logging
from pathlib import Path

from alist_sdk.models import Resp, Storage
from alist_sdk.client import Client
from alist_sdk.tools.models import Configs

logger = logging.getLogger("alist-sdk.tools")

__all__ = [
    "import_configs_from_dict",
    "import_configs_from_json_str",
    "import_configs_from_json_file",
    "export_configs",
    "export_configs_to_dict",
    "export_configs_to_json",
]


def __printf(key, data, res: Resp):
    """记录"""
    name = (
        ""
        if isinstance(data, list)
        else (data.get("mount_path") or data.get("path") or data.get("username"))
    )
    if res.code == 200:
        print(f"created {key} [{name}]")
    else:
        print(f"Error: {key} [{name}]: {res.code}: {res.message}")


def import_configs_from_dict(client: Client, configs: dict):
    """从JSON中导入配置"""
    apis = {
        "settings": "/api/admin/setting/save",
        "users": "/api/admin/user/create",
        "storages": "/api/admin/storage/create",
        "metas": "/api/admin/meta/create",
    }

    for k, vs in configs.items():
        if k == "settings":
            res = client.verify_request("POST", apis[k], json=vs)
            __printf(k, vs, res)
            continue
        else:
            for v in vs:
                v: dict
                if k == "storages" and v.get("driver", "") == "Local":
                    continue
                v.pop("id", None)
                res = client.verify_request("POST", apis[k], json=v)
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
        "settings": client.admin_setting_list().data,
        "users": client.admin_user_list().data.content,
        "storages": client.admin_storage_list().data.content,
        "metas": client.admin_meta_list().data.content,
    }
    return Configs(**apis)


def export_configs_to_dict(client: Client, *args, **kwargs) -> dict:
    return export_configs(client).model_dump(*args, **kwargs)


def export_configs_to_json(client: Client, *args, **kwargs) -> str:
    return export_configs(client).model_dump_json(*args, **kwargs)


def copy_configs(source_client: Client, target_client: Client):
    """"""
    return import_configs_from_dict(
        target_client,
        export_configs_to_dict(source_client),
    )


def copy_storages(source_client: Client, target_client: Client, *storage_names):
    """"""
    storages: list[Storage] = source_client.admin_storage_list().data.content
    if not storage_names:
        storage_names = [_.mount_path.strip("/") for _ in storages]
    for _s in storages:
        if _s.mount_path.strip("/") not in storage_names:
            continue
        target_client.admin_storage_create(_s)
