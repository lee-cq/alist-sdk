#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : app.py
@Author     : LeeCQ
@Date-Time  : 2024/9/15 22:55
"""
import typer

from alist_sdk.cmd.base import cnf
from alist_sdk.cmd.fs import fs
from alist_sdk.cmd.admin import admin
from alist_sdk.cmd.auth import auth


app = typer.Typer()

app.add_typer(auth, name="auth")
app.add_typer(fs, name="fs")
app.add_typer(admin, name="admin")


@app.command("version")
def version():
    """
    Show the version of alist-sdk.
    """
    from alist_sdk import __version__

    typer.echo(f"alist-sdk version: {__version__}")


@app.command("server-version")
def server_version(server: str = None):
    """
    Show the version of alist-server.
    """
    from alist_sdk import Client

    if server and server not in cnf.auth_data:
        return typer.echo("尚未登录到该服务器，请先登录 [cmd: alist-cli auth login].")

    if not server:
        server = cnf.auth_data.keys()
    else:
        server = [server]

    typer.echo("Server Version:")
    for s in server:
        client = cnf.get_client(s)
        typer.echo(f"{s}: {client.service_version}")
