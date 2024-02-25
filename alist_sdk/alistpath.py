#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : alistpath.py
@Author     : LeeCQ
@Date-Time  : 2024/2/25 12:40

"""
import os
import posixpath

from posixpath import *

__all__ = [*posixpath.__all__, "splitroot"]


def splitroot(p):
    """Split a pathname into drive, root and tail. On Posix, drive is always
    empty; the root may be empty, a single slash, or two slashes. The tail
    contains anything after the root. For example:

        splitroot('foo/bar') == ('', '', 'foo/bar')
        splitroot('/foo/bar') == ('', '/', 'foo/bar')
        splitroot('//foo/bar') == ('', '//', 'foo/bar')
        splitroot('///foo/bar') == ('', '/', '//foo/bar')
        splitroot('http://server/path/to/file') == ('http://server', '/', 'path/to/file')
    """
    p = os.fspath(p)
    if isinstance(p, bytes):
        sep = b"/"
        empty = b""
    else:
        sep = "/"
        empty = ""

    if p.startswith("http://") or p.startswith("https://"):
        # Absolute path, e.g.: 'http://server/path/to/file'
        return "/".join(p.split("/", 3)[:3]), "/", p.split("/", 3)[-1]

    elif p[:1] != sep:
        # Relative path, e.g.: 'foo'
        return empty, empty, p

    elif p[1:2] != sep or p[2:3] == sep:
        # Absolute path, e.g.: '/foo', '///foo', '////foo', etc.
        return empty, sep, p[1:]

    else:
        # Precisely two leading slashes, e.g.: '//foo'. Implementation defined per POSIX, see
        # https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html#tag_04_13
        return empty, p[:2], p[2:]
