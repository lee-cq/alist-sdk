#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : base.py
@Author     : LeeCQ
@Date-Time  : 2024/9/15 22:47
"""
import hashlib
import os
import time
from pathlib import Path

import typer
from pydantic import BaseModel

from alist_sdk import Client, login_server, AlistPath

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


class PWD(BaseModel):
    ppid: int
    ctime: float
    pwd: str


class CmdConfig(BaseModel):
    # 登陆数据
    auth_data: dict[str, Auth] = {}

    # # 路径数据
    # base_path: dict[str, str] = {}

    # alist-cli远程工作路径数据 -
    # 于父进程PID绑定，有效期6小时
    pwd_path: dict[str, PWD] = {}

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
        name: str,
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

        self.auth_data[name] = Auth(
            host=host,
            token=token,
            username=username,
            password=password,
            last_login=int(time.time()),
        )
        self.save_config()
        typer.echo(f"login success, token: {self.auth_data[name].token}")

    def remove_auth(self, name: str):
        if name not in self.auth_data:
            typer.echo(f"name {name} not found in auth data")
            return
        host = self.auth_data[name].host
        del self.auth_data[name]
        self.save_config()
        typer.echo(f"logout success, host: {host}")

    def get_client(self, name: str) -> Client:
        if name not in self.auth_data:
            raise ValueError(f"name [{name}] not found in auth data")
        t_info = self.auth_data[name]
        if int(time.time()) - t_info.last_login > 3600 * 24:
            self.add_auth(name, t_info.host, t_info.username, t_info.password)
        return login_server(t_info.host, token=self.auth_data[name].token)

    # def set_base_path(self, base_path: str, name: str = ""):
    #     self.base_path[name] = base_path
    #     self.save_config()
    #     typer.echo(f"set base path success, base path: {self.base_path}")

    # def remove_base_path(self, name: str):
    #     if name not in self.base_path:
    #         typer.echo(f"base path {name} not found in config")
    #         return
    #     del self.base_path[name]
    #     self.save_config()
    #     typer.echo(f"remove base path success, base path: {self.base_path}")

    # def get_base_path(self, name: str = ""):
    #     if name not in self.auth_data and name not in self.base_path:
    #         typer.echo(f"base path {name} not found in config", err=True)
    #         exit(1)
    #     if name not in self.base_path:
    #         return self.auth_data[name].host
    #     return self.base_path["name"]

    def clear_pwd(self):
        for ppid, p in self.pwd_path.items():
            if time.time() - p.ctime > 6 * 3600:
                del self.pwd_path[ppid]

    def set_pwd(self, pwd):
        """设置Pwd"""
        self.clear_pwd()
        # TODO 父进程不稳定
        self.pwd_path["0"] = PWD(ctime=time.time(), ppid=os.getppid(), pwd=pwd)
        self.save_config()

    def get_pwd(self):
        """获取pwd, 默认 /"""
        self.clear_pwd()
        _pwd = self.pwd_path.get("0")
        if _pwd is None:
            return "/"
        self.get_client(self.get_auth_name(_pwd.pwd))
        return _pwd.pwd

    def get_auth_name(self, url):
        """通过主机获取name"""
        host = "/".join(url.split("/", maxsplit=3)[:3])
        for name, ap in self.auth_data.items():
            if ap.host == host:
                return name
        raise ValueError(f"PWD [{url}] 没有登陆.")


cnf = CmdConfig.load_config()


class CmdPath:
    def __new__(cls, *args, **kwargs) -> AlistPath | Path:
        """
        //base_path/name/file.txt -- 有名称的基于base_path的路径
        ///name/file.txt          -- 无名称的基于base_path的路径
        //./name/file.txt         -- 基于alist_cli_pwd变量的路径
        name/file.txt             -- 本地相对路径
        /name/file.txt            -- 本地绝对路径
        """
        if args[0].startswith("//./"):
            rpath = args[0][4:]
            ppath = cnf.get_pwd()
            if ppath == "/":
                raise ValueError("未找到pwd信息。 先使用alist-cli fs cd 设置")
            return AlistPath(ppath, rpath, *args[1:], **kwargs)

        if args[0].startswith("//"):
            name, rp = args[0][2:].split("/", 1)
            if name == "":
                name = "default"
            cnf.get_client(name)
            return AlistPath(cnf.auth_data[name].host, rp, *args[1:], **kwargs)

        if args[0].startswith("https://") or args[0].startswith("http://"):
            cnf.get_client(cnf.get_auth_name(args[0]))
            return AlistPath(*args, **kwargs)

        return Path(*args, **kwargs)
