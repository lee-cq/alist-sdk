#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : __main__.py
@Author     : LeeCQ
@Date-Time  : 2024/8/23 23:42
"""
import json
from pathlib import Path

import typer

from alist_sdk.client import Client
from alist_sdk.path_lib import AlistPath, login_server


app = typer.Typer()
fs = typer.Typer()
admin = typer.Typer()

app.add_typer(fs, name="fs")
app.add_typer(admin, name="admin")


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


class Auth:
    def __init__(self):
        self.auth_file = Path(__file__).parent.joinpath("auth.json")
        self.auth_data = (
            json.loads(self.auth_file.read_text()) if self.auth_file.exists() else {}
        )
        for h, t in self.auth_data.items():
            if t:
                login_server(h, token=t)

    def add(
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

        self.auth_data[host] = token
        self.auth_file.write_text(json.dumps(self.auth_data))
        typer.echo(f"login success, token: {self.auth_data[host]}")

    def remove(self, host: str):
        host = host.strip("/")
        if host not in self.auth_data:
            typer.echo(f"host {host} not found in auth data")
            return
        del self.auth_data[host]
        self.auth_file.write_text(json.dumps(self.auth_data))
        typer.echo(f"logout success, host: {host}")

    def get_client(self, host: str):
        host = host.strip("/")
        if host not in self.auth_data:
            raise ValueError(f"host {host} not found in auth data")
        return login_server(host, token=self.auth_data[host])


auth = Auth()


@app.command("login")
def login(host: str, username: str, password: str):
    """登录, 创建或添加一个更新的token到本地"""
    auth.add(host, username=username, password=password)


@app.command("logout")
def logout(host: str):
    """登出, 删除本地的token"""
    auth.remove(host)


@fs.command("ls")
def fs_ls(
    path: str,
):
    """列出文件系统"""
    path = AlistPath(path)
    ls = path.iterdir() if path.is_dir() else [path]
    # type, size, modify_time, name
    total_size = 0
    for p in ls:
        total_size += p.stat().size
        p_type = "dir" if p.is_dir() else "file"
        typer.echo(
            f"{p_type:<8}"
            f"{beautify_size(p.stat().size):<10}"
            f"{p.stat().modified.strftime('%Y-%m-%d %H:%M:%S'):<20} {p.name}"
        )
    typer.echo(f"total: {beautify_size(total_size)}")


def fs_read(path: str):
    """读取文件内容"""
    path = AlistPath(path)
    with path.read_bytes() as f:
        return f.read()


app()
