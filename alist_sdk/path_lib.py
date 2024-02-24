"""Path Lib 类实现

像使用Path一样的易于使用Alist中的文件
"""
import fnmatch
import os
import posixpath
import re
import sys
from pathlib import PurePosixPath, PurePath
from functools import lru_cache, cached_property
from urllib.parse import quote_from_bytes as urlquote_from_bytes
from typing import Iterator

from pydantic import BaseModel
from httpx import URL

from alist_sdk import AlistError, RawItem
from alist_sdk.client import Client


class AlistServer(BaseModel):
    server: str
    token: str
    kwargs: dict = {}


ALIST_SERVER_INFO: dict[str, AlistServer] = dict()


def login_server(
        server: str,
        token=None,
        username=None,
        password=None,
        has_opt=False,
        **kwargs,
):
    """"""
    if token is None:
        client = Client(
            server,
            username=username,
            password=password,
            has_opt=has_opt,
            **kwargs,
        )
        token = client.headers.get("Authorization")
    ALIST_SERVER_INFO[server] = AlistServer(
        server=server,
        token=token,
        kwargs=kwargs,
    )


# noinspection PyMethodMayBeStatic
class _AlistFlavour:
    sep = "/"
    altsep = ""
    has_drv = True
    pathmod = posixpath

    is_supported = True

    def __init__(self):
        self.join = self.sep.join

    def parse_parts(self, parts):
        parsed = []
        sep = self.sep
        altsep = self.altsep
        drv = root = ""

        it = reversed(parts)
        for part in it:
            if not part:
                continue
            if altsep:
                part = part.replace(altsep, sep)
            drv, root, rel = self.splitroot(part)
            if sep in rel:
                for x in reversed(rel.split(sep)):
                    if x and x != ".":
                        parsed.append(sys.intern(x))
            else:
                if rel and rel != ".":
                    parsed.append(sys.intern(rel))
            if drv or root:
                if not drv:
                    # If no drive is present, try to find one in the previous
                    # parts. This makes the result of parsing e.g.
                    # ("C:", "/", "a") reasonably intuitive.
                    # noinspection PyAssignmentToLoopOrWithParameter
                    for part in it:
                        if not part:
                            continue
                        if altsep:
                            part = part.replace(altsep, sep)
                        drv = self.splitroot(part)[0]
                        if drv:
                            break
                break
        if drv or root:
            parsed.append(drv + root)
        parsed.reverse()
        return drv, root, parsed

    def join_parsed_parts(self, drv, root, parts, drv2, root2, parts2):
        """
        Join the two paths represented by the respective
        (drive, root, parts) tuples.  Return a new (drive, root, parts) tuple.
        """
        if root2:
            if not drv2 and drv:
                return drv, root2, [drv + root2] + parts2[1:]
        elif drv2:
            if drv2 == drv or self.casefold(drv2) == self.casefold(drv):
                # Same drive => second path is relative to the first
                return drv, root, parts + parts2[1:]
        else:
            # Second path is non-anchored (common case)
            return drv, root, parts + parts2
        return drv2, root2, parts2

    def splitroot(self, part, sep=sep):
        if part and part[0] == sep:
            stripped_part = part.lstrip(sep)
            # According to POSIX path resolution:
            # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap04.html#tag_04_11
            # "A pathname that begins with two successive slashes may be
            # interpreted in an implementation-defined manner, although more
            # than two leading slashes shall be treated as a single slash".
            if len(part) - len(stripped_part) == 2:
                return "", sep * 2, stripped_part
            else:
                return "", sep, stripped_part
        else:
            return "", "", part

    def casefold(self, s):
        return s

    def casefold_parts(self, parts):
        return parts

    def compile_pattern(self, pattern):
        return re.compile(fnmatch.translate(pattern)).fullmatch

    def make_uri(self, path):
        # We represent the path using the local filesystem encoding,
        # for portability to other applications.
        bpath = bytes(path)
        return "file://" + urlquote_from_bytes(bpath)


# noinspection PyProtectedMember,PyUnresolvedReferences
class PureAlistPath(PurePosixPath):
    _flavour = _AlistFlavour()

    @classmethod
    def _parse_args(cls, args):
        # This is useful when you don't want to create an instance, just
        # canonicalize some constructor arguments.
        parts = []
        for a in args:
            if isinstance(a, PurePath):
                parts += a._parts
            else:
                a = os.fspath(a)
                if isinstance(a, str):
                    # Force-cast str subclasses to str (issue #21127)
                    parts.append(str(a))
                else:
                    raise TypeError(
                        "argument should be a str object or an os.PathLike "
                        "object returning str, not %r" % type(a)
                    )
        return cls._flavour.parse_parts(parts)

    @classmethod
    def _from_parts(cls, args):
        # We need to call _parse_args on the instance, to get the
        # right flavour.
        args = list(args)
        self = object.__new__(cls)
        if isinstance(args[0], str) and args[0].startswith("http"):
            _u = URL(args[0])
            server = (
                f"{_u.scheme}://{_u.host}:{_u.port}".replace(":80", "")
                .replace(":443", "")
                .replace(":None", "")
            )
            args[0] = _u.path
        elif isinstance(args[0], cls):
            server = args[0].server
        else:
            server = ""

        drv, root, parts = self._parse_args(args)
        self._drv = drv or server
        self._root = root
        self._parts = parts
        self.server = server
        return self

    @classmethod
    def _from_parsed_parts(cls, drv, root, parts):
        self = object.__new__(cls)
        self._drv = drv
        self._root = root
        self._parts = parts
        return self

    def _make_child(self, args):
        drv, root, parts = self._parse_args(args)
        drv, root, parts = self._flavour.join_parsed_parts(
            self._drv, self._root, self._parts, drv, root, parts
        )
        return self._from_parsed_parts(drv, root, parts)

    def __new__(cls, *args):
        return cls._from_parts(args)

    def as_posix(self) -> str:
        return str(self).replace(self.drive, "")

    def as_uri(self):
        if not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        return str(self)

    def relative_to(self, *other):
        raise NotImplementedError("AlistPath不支持relative_to")


class AlistPath(PureAlistPath):
    """"""

    @cached_property
    def _client(self) -> Client:
        if self.drive == "":
            raise AlistError("当前对象没有设置server")

        try:
            _server = ALIST_SERVER_INFO[self.drive]
            return Client(
                _server.server,
                token=_server.token,
                **_server.kwargs,
            )
        except KeyError:
            raise AlistError(f"当前服务器[{self.drive}]尚未登陆")

    # def is_absolute(self) -> bool:
    def as_download_uri(self):
        if not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        if self.is_dir():
            raise IsADirectoryError()
        return self.drive + "/d" + self.as_posix() + "?sign=" + self.stat().sign

    @lru_cache()
    def stat(self) -> RawItem:
        _raw = self._client.get_item_info(self.as_posix())
        if _raw.code == 200:
            data = _raw.data
            return data
        if _raw.code == 500 and (
                "object not found" in _raw.message or "storage not found" in _raw.message
        ):
            raise FileNotFoundError(_raw.message)
        raise AlistError(_raw.message)

    def is_dir(self):
        """"""
        return self.stat().is_dir

    def is_file(self):
        """"""
        return not self.stat().is_dir

    def is_link(self):
        raise NotImplementedError("AlistPath不支持连接.")

    def exists(self):
        """"""
        try:
            return bool(self.stat())
        except FileNotFoundError:
            return False

    def iterdir(self) -> Iterator["AlistPath"]:
        """"""
        if not self.is_dir():
            raise

        for item in (
                self._client.list_files(self.as_posix(), refresh=True).data.content or []
        ):
            yield self.joinpath(item.name)

    def read_text(self):
        """"""
        return self._client.get(self.as_download_uri(), follow_redirects=True).text

    def read_bytes(self):
        """"""
        return self._client.get(self.as_download_uri(), follow_redirects=True).content

    def write_text(self, data: str, as_task=False):
        """"""
        return self.write_bytes(data.encode(), as_task=as_task)

    def write_bytes(self, data: bytes, as_task=False):
        """"""

        _res = self._client.upload_file_put(data, self.as_posix(), as_task=as_task)
        if _res.code == 200:
            return self.stat()
        return None
