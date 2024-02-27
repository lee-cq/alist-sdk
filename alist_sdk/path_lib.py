"""Path Lib 类实现

像使用Path一样的易于使用Alist中的文件
"""

from functools import lru_cache, cached_property
from typing import Iterator, Annotated, Any

from pydantic import BaseModel
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from alist_sdk import alistpath
from alist_sdk.py312_pathlib import PurePosixPath
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


class PureAlistPath(PurePosixPath):
    _flavour = alistpath

    # def __get_pydantic_core_schema__(self, source_type: Any, handler):
    #     """"""

    def is_absolute(self):
        """True if the path is absolute (has both a root and, if applicable,
        a drive)."""
        if self._flavour is alistpath:
            # ntpath.isabs() is defective - see GH-44626.
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

    def re_stat(self) -> RawItem:
        self.stat.cache_clear()
        return self.stat()

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
        raise AlistError()

    def mkdir(self, parents=False, exist_ok=False):
        """"""
        if parents:
            raise NotImplementedError("AlistPath不支持递归创建目录")
        if self.exists():
            if exist_ok:
                return
            raise FileExistsError(f"相同名称已存在: {self.as_posix()}")
        return self._client.mkdir(self.as_posix())

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
        _data = self._client.remove(self.parent.as_posix(), self.name)
        if _data.code != 200:
            raise AlistError(_data.message)

    def rmdir(self, missing_ok=False):
        """"""
        if not self.exists():
            if missing_ok:
                return
            raise FileNotFoundError(f"文件不存在: {self.as_posix()}")
        _data = self._client.remove_empty_directory(self.as_posix())
        if _data.code != 200:
            raise AlistError(_data.message)

    def rename(self, target: "AlistPath"):
        """"""
        if self == target:
            return
        if not self.exists():
            raise FileNotFoundError(f"文件不存在: {self.as_uri()}")

        if self.parent != target.parent:
            _data = self._client.move(
                self.parent.as_posix(),
                target.parent.as_posix(),
                self.name,
            )
            if _data.code != 200:
                raise AlistError(_data.message)

        if self.name != target.name:
            _data = self._client.rename(
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
