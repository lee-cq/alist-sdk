"""Path Lib 类实现

像使用Path一样的易于使用Alist中的文件
"""

import time
from functools import cached_property
from pathlib import Path
from typing import Iterator, Annotated, Any

from httpx import URL
from pydantic import BaseModel
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from alist_sdk import alistpath
from alist_sdk.models import Item, RawItem
from alist_sdk.err import AlistError
from alist_sdk.py312_pathlib import PurePosixPath
from alist_sdk.client import Client


class AlistServer(BaseModel):
    server: str
    token: str
    kwargs: dict = {}


ALIST_SERVER_INFO: dict[tuple[str, str, int], Client] = dict()


def login_server(
    server: str | Client,
    token=None,
    username=None,
    password=None,
    has_opt=False,
    **kwargs,
) -> Client:
    """"""

    if isinstance(server, str):
        _so = URL(server)
        server_info = _so.scheme, _so.host, _so.port
        if server_info in ALIST_SERVER_INFO:
            return ALIST_SERVER_INFO[server_info]

        _client = Client(
            server,
            token=token,
            username=username,
            password=password,
            has_opt=has_opt,
            **kwargs,
        )

    else:
        _client = server
    ALIST_SERVER_INFO[_client.server_info] = _client
    return _client


class PureAlistPath(PurePosixPath):
    _flavour = alistpath

    def __repr__(self):
        return "{}({!r})".format(
            self.__class__.__name__,
            self.as_uri() if self.is_absolute() else self.as_posix(),
        )

    def is_absolute(self):
        """True if the path is absolute (has both a root and, if applicable,
        a drive)."""
        if self._flavour is alistpath:
            return bool(self.drive and self.root)

        else:
            return self._flavour.isabs(str(self))

    def as_posix(self) -> str:
        return str(self).replace(self.drive, "")

    def as_uri(self):
        if not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        return str(self)

    def relative_to(self, other, /, *_deprecated, walk_up=False) -> str:
        other = self.with_segments(other, *_deprecated)
        for step, path in enumerate([other] + list(other.parents)):
            if self.is_relative_to(path):
                break

            elif path.name == "..":
                raise ValueError(f"'..' segment in {str(other)!r} cannot be walked")

        else:
            raise ValueError(f"{str(self)!r} and {str(other)!r} have different anchors")
        # noinspection PyProtectedMember
        parts = [".."] * step + self._tail[len(path._tail) :]
        return PurePosixPath(*parts).as_posix()

    # def match(self, path_pattern, *, case_sensitive=True):
    #     _pps = path_pattern.split("**")
    #
    #     return self._flavour.fnmatch(str(self), path_pattern, case_sensitive)


class AlistPath(PureAlistPath):
    """"""

    def __init__(
        self,
        *args,
        username: str = None,
        password: str = None,
        token: str = None,
        **kwargs,
    ):
        super().__init__(*args)
        if username:
            login_server(
                self.drive, username=username, password=password, token=token, **kwargs
            )

    @classmethod
    def from_client(cls, client: Client, path: str | PurePosixPath) -> "AlistPath":
        """从客户端实例构造

        :param client: 客户端实例
        :param path: （可能）位于该实例的绝对路径
        """
        if not isinstance(client, Client):
            raise TypeError()

        if not str(path).startswith("/"):
            raise ValueError(f"path必须是一个绝对路径 {path = }")

        if client.server_info not in ALIST_SERVER_INFO:
            login_server(client)

        f_path = client.base_url.join(path)
        return cls(f_path.__str__())

    @cached_property
    def client(self) -> Client:
        if self.drive == "":
            raise AlistError("当前对象没有设置server")

        try:
            _u = URL(self.drive)
            _server_info = _u.scheme, _u.host, _u.port
            return ALIST_SERVER_INFO[_server_info]
        except KeyError:
            raise AlistError(
                f"当前服务器[{self.drive}]尚未登陆。\n"
                f"使用AlistPath.from_client构造。\n"
                f"或构造AlistPath时传入username等相关信息。"
            )

    # def is_absolute(self) -> bool:
    def get_download_uri(self) -> str:
        if not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        if self.is_dir():
            raise IsADirectoryError()
        return self.raw_stat().raw_url

    def as_download_uri(self):
        return self.get_download_uri()

    def raw_stat(self, retry=1, timeout=0.1) -> RawItem:
        try:
            _raw = self.client.get_item_info(self.as_posix())
            if _raw.code == 200:
                data = _raw.data
                self.set_stat(data)
                return data
            if _raw.code == 500 and (
                "object not found" in _raw.message
                or "storage not found" in _raw.message
            ):
                raise FileNotFoundError(_raw.message)
            raise AlistError(_raw.message)
        except FileNotFoundError as _e:
            if retry > 0:
                time.sleep(timeout)
                return self.raw_stat(retry - 1)
            raise _e

    def stat(self) -> Item | RawItem:
        def f_stat() -> Item | RawItem:
            _r = (
                self.client.get_item_info(self.as_posix()).data
                if self.as_posix() == "/"
                else self.client.dict_files_items(self.parent.as_posix()).get(self.name)
            )

            if not _r:
                raise FileNotFoundError(f"文件不存在: {self.as_posix()} ")
            self.set_stat(_r)
            return _r

        _stat = getattr(self, "_stat", None)
        if isinstance(_stat, Item | RawItem):
            return _stat

        return f_stat()

    def set_stat(self, value: RawItem | Item):
        # noinspection PyAttributeOutsideInit
        self._stat = value

    def re_stat(self, retry=2, timeout=1) -> Item:
        if hasattr(self, "_stat"):
            delattr(self, "_stat")
        # self.client.list_files(self.parent.as_posix(), per_page=1, refresh=True)
        return self.raw_stat(retry=retry, timeout=timeout)

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
            return bool(self.re_stat())
        except FileNotFoundError:
            return False

    def iterdir(self) -> Iterator["AlistPath"]:
        """"""
        if not self.is_dir():
            raise

        for item in self.client.dict_files_items(
            self.as_posix(), refresh=True
        ).values():
            _ = self.joinpath(item.name)
            _.set_stat(item)
            yield _

    def read_text(self):
        """"""
        return self.client.get(
            self.as_download_uri(),
            follow_redirects=True,
            headers={"authorization": ""},
        ).text

    def read_bytes(self):
        """"""
        return self.client.get(
            self.as_download_uri(),
            follow_redirects=True,
            headers={"authorization": ""},
        ).content

    def write_text(self, data: str, as_task=False):
        """"""
        return self.write_bytes(data.encode(), as_task=as_task)

    def write_bytes(self, data: bytes | Path, as_task=False):
        """"""

        _res = self.client.upload_file_put(data, self.as_posix(), as_task=as_task)
        if _res.code == 200:
            return self.re_stat()
        raise AlistError()

    def mkdir(self, parents=False, exist_ok=False):
        """"""
        if self.exists():
            if exist_ok:
                return
            raise FileExistsError(f"相同名称已存在: {self.as_posix()}")

        if parents is False and not self.parent.exists():
            raise FileNotFoundError()

        return self.client.mkdir(self.as_posix())

    def touch(self, exist_ok=True):
        """"""
        if not exist_ok and self.exists():
            raise FileExistsError(f"文件已存在: {self.as_posix()}")
        return self.write_bytes(b"", as_task=False)

    def unlink(self, missing_ok=False):
        """"""
        if not self.exists():
            if missing_ok:
                return
            raise FileNotFoundError(f"文件不存在: {self.as_posix()}")
        _data = self.client.remove(self.parent.as_posix(), self.name)
        if _data.code != 200:
            raise AlistError(_data.message)

    def rmdir(self, missing_ok=False):
        """"""
        if not self.exists():
            if missing_ok:
                return
            raise FileNotFoundError(f"文件不存在: {self.as_posix()}")
        _data = self.client.remove_empty_directory(self.as_posix())
        if _data.code != 200:
            raise AlistError(_data.message)

    def rename(self, target: "AlistPath"):
        """"""
        if self == target:
            return
        if not self.exists():
            raise FileNotFoundError(f"文件不存在: {self.as_uri()}")

        if self.parent != target.parent:
            _data = self.client.move(
                self.parent.as_posix(),
                target.parent.as_posix(),
                self.name,
            )
            if _data.code != 200:
                raise AlistError(_data.message)

        if self.name != target.name:
            _data = self.client.rename(
                target.name,
                target.parent.joinpath(self.name).as_posix(),
            )
            if _data.code != 200:
                raise AlistError(_data.message)

        return target


class AlistPathPydanticAnnotation:
    @classmethod
    def validate_alist_path(cls, v: Any, handler) -> AlistPath:
        if isinstance(v, AlistPath):
            return v
        s = handler(v)
        return AlistPath(s)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, _handler
    ) -> core_schema.CoreSchema:
        assert source_type is AlistPath
        return core_schema.no_info_wrap_validator_function(
            cls.validate_alist_path,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class AbsAlistPathPydanticAnnotation(AlistPathPydanticAnnotation):
    @classmethod
    def validate_alist_path(cls, v: Any, handler) -> AlistPath:
        _path = super().validate_alist_path(v, handler)
        if _path.drive:
            return _path
        else:
            raise ValueError("Invalid AlistPath")


AlistPathType = Annotated[AlistPath, AlistPathPydanticAnnotation]

AbsAlistPathType = Annotated[AlistPath, AbsAlistPathPydanticAnnotation]
