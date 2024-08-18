# 测试 path_lib.py
import time

import pytest

from alist_sdk.path_lib import PureAlistPath, AlistPath, login_server
from tests.test_client import DATA_DIR


class TestPureAlistPath:
    def test_pure_alist_path(self):
        path = PureAlistPath("https://server:5245/path/to/file")
        # 属性
        assert path.parts == ("https://server:5245/", "path", "to", "file")
        assert path.drive == "https://server:5245"
        assert path.root == "/"
        assert path.anchor == "https://server:5245/"
        assert path.parent == PureAlistPath("https://server:5245/path/to")
        assert path.name == "file"
        assert path.suffix == ""
        assert path.suffixes == []
        assert path.stem == "file"

    def test_pure_alist_path_method(self):
        path = PureAlistPath("https://server/path/to/file")

        assert path.as_posix() == "/path/to/file"
        assert path.as_uri() == "https://server/path/to/file"

        assert path.joinpath("another") == PureAlistPath(
            "https://server/path/to/file/another"
        )
        assert path.joinpath("another", "file", "path") == PureAlistPath(
            "https://server/path/to/file/another/file/path"
        )
        assert path.joinpath("another/file/path") == PureAlistPath(
            "https://server/path/to/file/another/file/path"
        )

    def test_relative_to(self):
        path = PureAlistPath("https://server/path/to/file")
        p = PureAlistPath("https://server/path")

        assert path.relative_to(p) == ("to/file")


class TestAlistPath:
    def setup_class(self):
        self.client = login_server(
            "http://localhost:5245",
            username="admin",
            password="123456",
        )
        DATA_DIR.joinpath("test.txt").write_text("123")

    def setup_method(self):
        self.client._cached_path_list = {}

    def test_login(self):
        _c = AlistPath("http://localhost:5245/", username="admin", password="123456")
        assert _c.is_dir()

    def test_read_text(self):
        DATA_DIR.joinpath("test.txt").write_text("123")
        path = AlistPath("http://localhost:5245/local/test.txt")
        assert path.read_text() == "123"

    def test_alist_path(self):
        path = AlistPath("http://localhost:5245/local/test.txt")
        assert path.read_bytes() == b"123"

    def test_write_text(self):
        path = AlistPath("http://localhost:5245/local/test_write_text.txt")
        path.write_text("123")
        assert DATA_DIR.joinpath("test_write_text.txt").read_text() == "123"

    def test_write_bytes(self):
        path = AlistPath("http://localhost:5245/local/test_write_bytes.txt")
        path.write_bytes(b"123")
        assert DATA_DIR.joinpath("test_write_bytes.txt").read_bytes() == b"123"

    def test_mkdir(self):
        dir_name = f"test_mkdir_{int(time.time())}"
        path = AlistPath(f"http://localhost:5245/local/{dir_name}")
        path.mkdir()
        assert DATA_DIR.joinpath(dir_name).is_dir()

    def test_touch(self):
        path = AlistPath("http://localhost:5245/local/test_touch.txt")
        path.touch()
        assert DATA_DIR.joinpath("test_touch.txt").exists()

    def test_unlink(self):
        DATA_DIR.joinpath("test_unlink.txt").write_text("123")
        path = AlistPath("http://localhost:5245/local/test_unlink.txt")
        path.unlink()
        assert not DATA_DIR.joinpath("test_unlink.txt").exists()

    @pytest.mark.skip("Alist 接口不生效")
    def test_rmdir(self):
        DATA_DIR.joinpath("test_rmdir").mkdir()
        path = AlistPath("http://localhost:5245/local/test_rmdir")
        path.rmdir()
        assert not DATA_DIR.joinpath("test_rmdir").exists()

    def test_rename(self):
        DATA_DIR.joinpath("test_rename.txt").write_text("123")
        path = AlistPath("http://localhost:5245/local/test_rename.txt")
        path.rename(AlistPath("http://localhost:5245/local/test_rename_new.txt"))
        assert not DATA_DIR.joinpath("test_rename.txt").exists()
        assert DATA_DIR.joinpath("test_rename_new.txt").read_text() == "123"

    def test_re_stat(self):
        DATA_DIR.joinpath("test_re_stat.txt").write_text("123")
        path = AlistPath("http://localhost:5245/local/test_re_stat.txt")
        assert path.stat().size == 3
        DATA_DIR.joinpath("test_re_stat.txt").write_text("1234")
        assert path.re_stat().size == 4

    def test_from_client(self):
        DATA_DIR.joinpath("test_from_client.txt").write_text("123")
        path = AlistPath.from_client(self.client, "/local/test_from_client.txt")
        assert path.exists()
        assert path.client is self.client


def test_pydantic():
    from pydantic import BaseModel
    from alist_sdk.path_lib import AlistPathType

    class T(BaseModel):
        p: AlistPathType

    T(p="https://leecq.cn")
    T(p="ss/c")


def test_abs_path():
    from pydantic import BaseModel
    from alist_sdk.path_lib import AbsAlistPathType

    class T(BaseModel):
        p: AbsAlistPathType

    T(p="https://leecq.cn")


@pytest.mark.xfail()
def test_abs_path_err():
    from pydantic import BaseModel
    from alist_sdk.path_lib import AbsAlistPathType

    class T(BaseModel):
        p: AbsAlistPathType

    T(p="ss/c")
