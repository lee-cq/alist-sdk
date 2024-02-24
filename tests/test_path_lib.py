# 测试 path_lib.py
from alist_sdk.path_lib import PureAlistPath, AlistPath, login_server


def test_pure_alist_path():
    path = PureAlistPath("https://server/path/to/file")
    # 属性
    assert path.server == "https://server"
    assert path.parts == ("/", "path", "to", "file")
    assert path.drive == "https://server"
    assert path.root == "/"
    assert path.anchor == "https://server/"
    assert path.parent == PureAlistPath("https://server/path/to")
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

