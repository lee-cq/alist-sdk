#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : app.py
@Author     : LeeCQ
@Date-Time  : 2024/9/15 22:55
"""
import typer

from alist_sdk.cmd.fs import fs
from alist_sdk.cmd.admin import admin
from alist_sdk.cmd.auth import auth


app = typer.Typer()

app.add_typer(auth, name="auth")
app.add_typer(fs, name="fs")
app.add_typer(admin, name="admin")
