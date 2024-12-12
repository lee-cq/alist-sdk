#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : admin.py
@Author     : LeeCQ
@Date-Time  : 2024/9/15 22:47
"""
import typer

from alist_sdk.cmd.base import cnf

admin = typer.Typer(name="admin", help="管理命令")


storage = typer.Typer(name="storage", help="存储管理")
admin.add_typer(storage, name="storage")


@storage.command("list")
def storage_list():
    """
    列出存储列表
    """

    client = cnf.get_client()
    res = client.admin_storage_list()
    typer.echo(res)


@storage.command("delete")
def storage_delete(
    storage_id=typer.Argument(..., help="存储ID, 通过alist-cli admin storage list获取")
):
    """
    创建存储
    """
    client = cnf.get_client()
    res = client.admin_storage_delete(storage_id)
    typer.echo(res)
