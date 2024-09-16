#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : auth.py
@Author     : LeeCQ
@Date-Time  : 2024/9/16 13:19
"""
import typer

from alist_sdk.cmd.base import cnf

auth = typer.Typer(name="auth", help="Authentication commands.")


@auth.command("login")
def login(host: str, username: str, password: str):
    """登录, 创建或添加一个更新的token到本地"""
    cnf.add_auth(host, username=username, password=password)


@auth.command("logout")
def logout(host: str):
    """登出, 删除本地的token"""
    cnf.remove_auth(host)


@auth.command("list")
def list_auth(token: bool = typer.Option(False, "--token", "-t", help="显示token")):
    """列出所有已登录的host"""
    if token:
        las = "\n".join(f"{host}: {_t}" for host, _t in cnf.auth_data.items())
    else:
        las = "\n".join(host for host in cnf.auth_data.keys())
    if not las:
        typer.echo("未登录到任何AlistServer")
        return
    typer.echo(f"已登录到的AlistServer:\n{las}")


@auth.command("refresh")
def refresh_token(host: str = typer.Argument(None, help="更新指定host的token")):
    """刷新token"""
