#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : base.py
@Author     : LeeCQ
@Date-Time  : 2024/9/15 22:47
"""
import hashlib
import time
from pathlib import Path

import typer
from pydantic import BaseModel

from alist_sdk import Client, login_server, AlistPath

text_types = "txt,htm,html,xml,java,properties,sql,js,md,json,conf,ini,vue,php,py,bat,gitignore,yml,go,sh,c,cpp,h,hpp,tsx,vtt,srt,ass,rs,lrc,yaml"

CMD_BASE_PATH = ""
CONFIG_FILE_PATH = Path.home().joinpath(".config", "alist_cli.json")


def beautify_size(byte_size: float):
    if byte_size < 1024:
        return f"{byte_size:.2f}B"
    byte_size /= 1024
    if byte_size < 1024:
        return f"{byte_size:.2f}KB"
    byte_size /= 1024
    if byte_size < 1024:
        return f"{byte_size:.2f}MB"
    byte_size /= 1024
    return f"{byte_size:.2f}GB"


def xor(s: str, key: str) -> str:
    """
    字符串的亦或加密/解密
    :param s: 待加密/解密的字符串
    :param key: 加密/解密密钥
    :return: 加密/解密后的字符串
    """
    key = hashlib.md5(key.encode("utf-8")).hexdigest()
    return "".join(
        [chr(ord(c) ^ ord(k)) for c, k in zip(s, key * (len(s) // len(key) + 1))]
    )


class Auth(BaseModel):
    host: str
    token: str
    username: str
    password: str
    last_login: int = 0


class CmdConfig(BaseModel):
    auth_data: dict[str, Auth] = {}
    base_path: dict[str, str] = {}

    @classmethod
    def load_config(cls):
        """加载配置"""

        if not CONFIG_FILE_PATH.exists():
            return cls()
        try:
            typer.echo(f"load config from {CONFIG_FILE_PATH}")
            return cls.model_validate_json(
                xor(
                    CONFIG_FILE_PATH.read_bytes().decode("utf-8"),
                    CONFIG_FILE_PATH.as_posix(),
                )
            )
        except Exception as e:
            typer.echo(f"load config failed, {e}")
            wait_info = (
                f"Do you want to remove the config file[{CONFIG_FILE_PATH}]? (y/n)"
            )
            if input(wait_info).lower() == "y":
                CONFIG_FILE_PATH.unlink()
                typer.echo(f"remove config file success, {CONFIG_FILE_PATH}")
            exit(1)

    def save_config(self):
        """保存配置"""
        CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        print(f"save config to {self.model_dump_json()}")
        CONFIG_FILE_PATH.write_bytes(
            xor(self.model_dump_json(), CONFIG_FILE_PATH.as_posix()).encode("utf-8"),
        )

    def add_auth(
        self,
        host: str,
        username: str = None,
        password: str = None,
        token: str = None,
    ):
        host = host.strip("/")
        if not token:
            try:
                _c = Client(host, username=username, password=password)
                if _c.login_username != username:
                    typer.echo(f"login failed, username: {_c.login_username}")
                    return
                token = _c.get_token()
            except Exception as e:
                typer.echo(f"login failed, {e}")
                return

        self.auth_data[host] = Auth(
            host=host,
            token=token,
            username=username,
            password=password,
            last_login=int(time.time()),
        )
        self.save_config()
        typer.echo(f"login success, token: {self.auth_data[host].token}")

    def remove_auth(self, host: str):
        host = host.strip("/")
        if host not in self.auth_data:
            typer.echo(f"host {host} not found in auth data")
            return
        del self.auth_data[host]
        self.save_config()
        typer.echo(f"logout success, host: {host}")

    def get_client(self, host: str):
        host = host.strip("/")
        if host not in self.auth_data:
            raise ValueError(f"host {host} not found in auth data")
        t_info = self.auth_data[host]
        if int(time.time()) - t_info.last_login > 3600 * 24:
            self.add_auth(host, t_info.username, t_info.password)
        return login_server(host, token=self.auth_data[host].token)

    def set_base_path(self, base_path: str, name: str = ""):
        self.base_path[name] = base_path
        self.save_config()
        typer.echo(f"set base path success, base path: {self.base_path}")

    def remove_base_path(self, name: str):
        if name not in self.base_path:
            typer.echo(f"base path {name} not found in config")
            return
        del self.base_path[name]
        self.save_config()
        typer.echo(f"remove base path success, base path: {self.base_path}")

    def get_base_path(self, name: str = ""):
        if name not in self.base_path:
            typer.echo(f"base path {name} not found in config", err=True)
            exit(1)
        return self.base_path[name]


cnf = CmdConfig.load_config()


class CmdPath:
    def __new__(cls, *args, **kwargs) -> AlistPath | Path:
        """
        //base_path/name/file.txt -- 有名称的基于base_path的路径
        ///name/file.txt          -- 无名称的基于base_path的路径
        name/file.txt             -- 本地相对路径
        /name/file.txt            -- 本地绝对路径
        """
        if args[0].startswith("//"):
            name, rp = args[0][2:].split("/", 1)
            return AlistPath(cnf.get_base_path(name), rp, *args[1:], **kwargs)

        return Path(*args, **kwargs)
