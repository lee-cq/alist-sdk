#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : fs.py
@Author     : LeeCQ
@Date-Time  : 2024/9/15 22:47
"""
from datetime import datetime
import subprocess
from pathlib import Path

import typer

from alist_sdk import AlistPath
from alist_sdk.cmd.base import beautify_size, CmdPath, cnf

fs = typer.Typer(name="fs", help="文件系统相关操作")


@fs.command("cd")
def cd(path: str):
    """设置一个pwd"""
    if path.startswith("./"):
        _p: AlistPath = CmdPath("//" + path)
    else:
        _p: AlistPath = CmdPath(path)

    if isinstance(_p, AlistPath) and _p.exists():
        cnf.set_pwd(_p.as_uri())
        typer.echo(f"cd {path} succeed. [{_p.as_uri()}]")
    else:
        typer.echo(f"CD Error. {path} -> {_p.as_uri()}", err=True)


@fs.command("pwd")
def pwd():
    _ = cnf.get_pwd()
    typer.echo(f"PWD: {_ if _ != '/' else 'Not Find.'}")


@fs.command("ls")
def ls(path: str):
    """列出文件系统"""
    path: AlistPath | Path = CmdPath(path)
    total_size = 0
    is_remote = isinstance(path, AlistPath)
    print(type(path), path)
    # type, size, modify_time, name
    for p in path.iterdir() if path.is_dir() else [path]:
        f_size = p.stat().st_size if is_remote or p.is_file() else 0
        total_size += f_size
        p_type = "dir" if p.is_dir() else "file"

        p_mtime = (
            p.stat().modified
            if is_remote
            else datetime.fromtimestamp(p.stat().st_mtime)
        )
        typer.echo(
            f"{p_type:<8}"
            f"{beautify_size(f_size):<10}"
            f"{p_mtime.strftime('%Y-%m-%d %H:%M:%S'):<20} {p.name}"
        )
    typer.echo(f"total: {beautify_size(total_size)}")


@fs.command("print")
def fs_read(path: str):
    """读取文件内容"""
    text_types = (
        "txt,md,log,conf,ini,yaml,json,xml,csv,tsv,list,lst,sh,bash,zsh,py,"
        "yaml,yml,java,c,cpp,h,hpp,go,php,js,css,html,jsp,jspx,asp,aspx,cs,"
        "vb,lua,pl,pm,rb,sql,bat,ps1,psm1,psd1"
    )
    path = AlistPath(path)
    _text_types = (
        {i.key: i.value for i in path.client.admin_setting_list(3).data}
        .get("text_types", text_types)
        .split(",")
    )
    if path.suffix not in _text_types:
        typer.echo(f"{path.suffix} 文件类型不支持直接读取")
    with path.read_bytes() as f:
        typer.echo(f"Read from {path.as_uri()}\n" + "=" * 50)
        typer.echo("\n" + f.read())


@fs.command("mkdir")
def mkdir(
    path: str = typer.Argument(..., help="父目录路径"),
    name: str = typer.Argument("", help="目录名称"),
    parents: bool = typer.Option(False, help="是否创建父目录"),
    exist_ok: bool = typer.Option(False, help="是否忽略已存在的目录"),
):
    """创建目录"""
    try:
        AlistPath(path).joinpath(name).mkdir(parents=parents, exist_ok=exist_ok)
    except Exception as e:
        typer.echo(f"mkdir error: {e}")


@fs.command("rm")
def rm(
    path: str,
    recursive: bool = typer.Option(False, "-r", help="是否递归删除"),
    force: bool = typer.Option(False, "-f", help="是否强制删除"),
):
    """删除文件或目录,"""
    try:
        path = AlistPath(path)
        if not recursive and path.is_dir() and len(list(path.iterdir())) != 0:
            typer.echo(f"{path} 不是空目录，请使用 -r 参数递归删除")
            return
        if not force:
            typer.echo(f"rm {path} ? (y/n)")
            if input().lower() not in ["y", "yes"]:
                return

        AlistPath(path).unlink(missing_ok=True)
    except Exception as e:
        typer.echo(f"rm error: {e}")


@fs.command("cp")
def cp(
    src: str,
    dst: str,
    recursive: bool = typer.Option(False, "-r", help="是否递归复制"),
):
    """复制文件 递归
    alist  - alist
    alist - local
    local - alist
    """


@fs.command("download")
def download(
    src: str,
    dst: str,
    recursive: bool = typer.Option(False, "-r", help="是否递归下载"),
):
    """下载文件"""

    def down_file(src_path, dst_path):
        down_link = AlistPath(src).as_download_uri()
        if Path(dst_path).exists():
            typer.echo(f"{dst_path} 已存在，跳过")
            return
        if not Path(dst_path).parent.exists():
            Path(dst_path).parent.mkdir(parents=True)
        typer.echo(f"downloading {src_path} to {dst_path}")
        subprocess.run(["curl", "-o", dst_path, down_link])  # TODO: 自定义UA

    src = AlistPath(src)
    dst = Path(dst)
    if src.is_dir():
        dst = dst.joinpath(src.name)
        dst.mkdir(parents=True, exist_ok=True)

    for p in src.iterdir():
        if p.is_dir() and recursive:
            download(str(p), str(dst.joinpath(p.name)))
        elif p.is_file():
            down_file(p, dst.joinpath(p.name))
        else:
            typer.echo(f"{p} 不是文件或目录，跳过")


@fs.command("upload")
def upload(
    src: str,
    dst: str,
    force: bool = typer.Option(False, help="是否覆盖已有文件"),
):
    """上传文件"""
    if not Path(src).exists() or not Path(src).is_file():
        typer.echo(f"{src} 不存在或不是文件")
        exit(1)
    if not AlistPath(dst).parent.exists():
        typer.echo(f"{AlistPath(dst).parent} 不存在")
        exit(1)
    if AlistPath(dst).exists() and not force:
        typer.echo(f"{dst} 已存在")
        exit(1)
    typer.echo(f"uploading {src} to {dst}")
    AlistPath(dst).write_bytes(Path(src))
