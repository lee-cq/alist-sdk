# 测试 path_lib.py


from alist_sdk.path_lib import PureAlistPath, AlistPath, login_server
from tests.test_client import DATA_DIR


class TestPureAlistPath:

    def test_pure_alist_path(self):
        path = PureAlistPath("https://server:5244/path/to/file")
        # 属性
        assert path.parts == ("https://server:5244/", "path", "to", "file")
        assert path.drive == "https://server:5244"
        assert path.root == "/"
        assert path.anchor == "https://server:5244/"
        assert path.parent == PureAlistPath("https://server:5244/path/to")
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


class TestAlistPath:

    def setup_class(self):
        login_server(
            "http://localhost:5244",
            username="admin",
            password="123456",
        )
        DATA_DIR.joinpath("test.txt").write_text("123")

    def test_read_text(self):
        path = AlistPath("http://localhost:5244/local/test.txt")
        assert path.read_text() == "123"

    def test_alist_path(self):
        path = AlistPath("http://localhost:5244/local/test.txt")
        assert path.read_bytes() == b"123"

    def test_write_text(self):
        path = AlistPath("http://localhost:5244/local/test_write_text.txt")
        path.write_text("123")
        assert DATA_DIR.joinpath("test_write_text.txt").read_text() == "123"

    def test_write_bytes(self):
        path = AlistPath("http://localhost:5244/local/test_write_bytes.txt")
        path.write_bytes(b"123")
        assert DATA_DIR.joinpath("test_write_bytes.txt").read_bytes() == b"123"

    def test_mkdir(self):
        path = AlistPath("http://localhost:5244/local/test_mkdir")
        path.mkdir()
        assert DATA_DIR.joinpath("test_mkdir").is_dir()

    def test_touch(self):
        path = AlistPath("http://localhost:5244/local/test_touch.txt")
        path.touch()
        assert DATA_DIR.joinpath("test_touch.txt").exists()

    def test_unlink(self):
        DATA_DIR.joinpath("test_unlink.txt").write_text("123")
        path = AlistPath("http://localhost:5244/local/test_unlink.txt")
        path.unlink()
        assert not DATA_DIR.joinpath("test_unlink.txt").exists()
