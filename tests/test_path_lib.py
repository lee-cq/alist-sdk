# 测试 path_lib.py

import sys

import pytest

from alist_sdk.path_lib import PureAlistPath, AlistPath, login_server

# 如果Python版本是3.12跳过模块
if sys.version_info >= (3, 12):
    pytest.skip("Skip this module on Python 3.12", allow_module_level=True)


def test_pure_alist_path():
    path = PureAlistPath("https://server:5244/path/to/file")
    # 属性
    assert path.server == "https://server:5244"
    assert path.parts == ("/", "path", "to", "file")
    assert path.drive == "https://server:5244"
    assert path.root == "/"
    assert path.anchor == "https://server:5244/"
    assert path.parent == PureAlistPath("https://server:5244/path/to")
    assert path.name == "file"
    assert path.suffix == ""
    assert path.suffixes == []
    assert path.stem == "file"


def test_pure_alist_path_method():
    path = PureAlistPath("https://server/path/to/file")

    assert path.as_posix() == "/path/to/file"
    assert path.as_uri() == "https://server/path/to/file"

    assert path.joinpath("another") == PureAlistPath("https://server/path/to/file/another")
    assert path.joinpath("another", "file", "path") == PureAlistPath("https://server/path/to/file/another/file/path")
    assert path.joinpath("another/file/path") == PureAlistPath("https://server/path/to/file/another/file/path")


def test_alist_path():
    from tests.test_client import DATA_DIR

    login_server("http://localhost:5244", username="admin", password="123456", )
    DATA_DIR.joinpath("test.txt").write_text("123")

    path = AlistPath("http://localhost:5244/local/test.txt")
    assert path.read_text() == "123"
    assert path.read_bytes() == b"123"
