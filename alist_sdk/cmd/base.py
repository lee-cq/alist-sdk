#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : base.py
@Author     : LeeCQ
@Date-Time  : 2024/9/15 22:47
"""
import time
from pathlib import Path

import typer
from pydantic import BaseModel

from alist_sdk import Client, login_server, AlistPath

text_types = "txt,htm,html,xml,java,properties,sql,js,md,json,conf,ini,vue,php,py,bat,gitignore,yml,go,sh,c,cpp,h,hpp,tsx,vtt,srt,ass,rs,lrc,yaml"

CMD_BASE_PATH = ""


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


def xor_encrypt(s: str, key: str) -> str:
    """
    字符串的亦或加密
    :param s: 待加密的字符串
    :param key: 加密密钥
    :return: 加密后的字符串
    """
    return "".join(
        [chr(ord(c) ^ ord(k)) for c, k in zip(s, key * (len(s) // len(key) + 1))]
    )


def xor_decrypt(s: str, key: str) -> str:
    """
    字符串的亦或解密
    :param s: 待解密的字符串
    :param key: 加密密钥
    :return: 解密后的字符串
    """
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
    auth: dict[str, Auth] = {}
    base_path: dict[str, str] = {}

    @classmethod
    def load_config(cls):
        """加载配置"""

        config_file = Path.home().joinpath(".config", "alist_cli.json")
        if not config_file.exists():
            return cls()
        try:
            return cls.model_validate_json(
                xor_decrypt(config_file.read_text(), str(config_file))
            )
        except Exception as e:
            typer.echo(f"load config failed, {e}")
            wait_info = f"Do you want to remove the config file[{config_file}]? (y/n)"
            if input(wait_info).lower() == "y":
                config_file.unlink()
                typer.echo(f"remove config file success, {config_file}")
            exit(1)

    def save_config(self):
        """保存配置"""
        Path.home().joinpath(".config").mkdir(parents=True, exist_ok=True)
        config_file = Path.home().joinpath(".config", "alist_cli.json")
        config_file.write_text(xor_encrypt(self.model_dump_json(), str(config_file)))

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

        self.auth[host] = Auth(
            host=host,
            token=token,
            username=username,
            password=password,
            last_login=int(time.time()),
        )
        self.save_config()
        typer.echo(f"login success, token: {self.auth[host].token}")

    def remove_auth(self, host: str):
        host = host.strip("/")
        if host not in self.auth:
            typer.echo(f"host {host} not found in auth data")
            return
        del self.auth[host]
        self.save_config()
        typer.echo(f"logout success, host: {host}")

    def get_client(self, host: str):
        host = host.strip("/")
        if host not in self.auth:
            raise ValueError(f"host {host} not found in auth data")
        t_info = self.auth[host]
        if int(time.time()) - t_info.last_login > 3600 * 24:
            self.add_auth(host, t_info.username, t_info.password, t_info.token)
        return login_server(host, token=self.auth[host])

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
