import asyncio
import pytest
from pathlib import Path

from alist_sdk import Client, Me, Item, RawItem, ListItem, Resp, Task, DirItem, AsyncClient

DATA_DIR = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST = Path(__file__).parent.joinpath('alist/test_dir_dst')
DATA_DIR_DST.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


def create_storage_local(client_, mount_name, local_path: Path):
    local_storage = {
        "mount_path": f"/{mount_name}",
        "order": 0,
        "driver": "Local",
        "cache_expiration": 0,
        "status": "work",
        "addition": "{\"root_folder_path\":\"%s\",\"thumbnail\":false,"
                    "\"thumb_cache_folder\":\"\",\"show_hidden\":true,"
                    "\"mkdir_perm\":\"750\"}" % local_path.absolute().as_posix(),
        "remark": "",
        "modified": "2023-11-20T15:00:31.608106706Z",
        "disabled": False,
        "enable_sign": False,
        "order_by": "name",
        "order_direction": "asc",
        "extract_folder": "front",
        "web_proxy": False,
        "webdav_policy": "native_proxy",
        "down_proxy_url": ""
    }
    if f'/{mount_name}' not in [
        i['mount_path'] for i in client_.get("/api/admin/storage/list").json()['data']['content']
    ]:
        assert client_.post(
            "/api/admin/storage/create",
            json=local_storage
        ).json().get('code') == 200, "创建Storage失败。"
    else:
        print("已经创建，跳过 ...")


def create_storage_dst():
    """"""


def clear_dir(path: Path):
    if not path.exists():
        return
    for item in path.iterdir():
        if item.is_dir():
            clear_dir(item)
        else:
            item.unlink()
    path.rmdir()


def setup_module() -> None:
    clear_dir(DATA_DIR)
    clear_dir(DATA_DIR_DST)
    DATA_DIR.mkdir(exist_ok=True)
    DATA_DIR_DST.mkdir(exist_ok=True)

    _client = Client('http://localhost:5244', username='admin', password='123456')
    create_storage_local(_client, 'local', DATA_DIR)
    create_storage_local(_client, 'local_dst', DATA_DIR_DST)


# noinspection PyMethodMayBeStatic
class TestSyncClient:
    __client = Client('http://localhost:5244', username='admin', password='123456')

    @property
    def client(self) -> Client:
        return self.__client

    def setup_method(self) -> None:
        print("--- setup_method ---")
        clear_dir(DATA_DIR)
        clear_dir(DATA_DIR_DST)
        DATA_DIR.mkdir(exist_ok=True)
        DATA_DIR_DST.mkdir(exist_ok=True)

    def run(self, func, *args, **kwargs):
        print("run", func.__name__, end=": ")
        res = func(*args, **kwargs)
        print("RESP: ", res)
        return res

    def test_login(self):
        _client = Client("http://localhost:5244", verify=False)
        assert _client.login(username='admin', password="123456", ), "登陆失败"

    def test_me(self):
        res = self.run(self.client.me)
        assert res.code == 200
        assert isinstance(res.data, Me), "数据结构错误。"

    def test_mkdir(self):
        res = self.run(
            self.client.mkdir, 
            '/local/test_mkdir'
        )
        assert res.code == 200
        assert DATA_DIR.joinpath('test_mkdir').exists(), "创建失败"

    def test_rename(self):
        source = DATA_DIR.joinpath('test_rename-s')
        dest = DATA_DIR.joinpath('test_rename-d')
        source.mkdir(exist_ok=True)
        clear_dir(dest)
        res = self.run(
            self.client.rename,
            'test_rename-d',
            '/local/test_rename-s'
        )
        assert res.code == 200
        assert dest.exists()
        assert not source.exists()

    @pytest.mark.skip
    def test_upload_file_from_data(self):
        data = b"test_data"
        alist_full_name = '/local/upload_file_form_data'
        path_file = DATA_DIR.joinpath('upload_file_form_data')
        res = self.run(
            self.client.upload_file_form_data,
            data, alist_full_name,
            as_task=False
        )
        assert res.data is None
        assert res.code == 200
        assert path_file.exists()

    def test_upload_put(self):
        alist_full_name = '/local/upload_file_form_data'
        alist_data_path = DATA_DIR.joinpath('upload_file_form_data')

        res = self.run(
            self.client.upload_file_put,
            __file__,
            alist_full_name,
            as_task=False
        )
        assert res.code == 200
        assert alist_data_path.exists()

    def test_list_dir(self):
        DATA_DIR.joinpath('test_list_dir_dir').mkdir()
        DATA_DIR.joinpath('test_list_dir_file').write_text('test')
        res = self.run(
            self.client.list_files,
            '/local',
        )
        assert res.code == 200
        assert isinstance(res.data, ListItem)
        assert isinstance(res.data.content[0], Item)

    def test_list_dir_null(self):
        DATA_DIR.joinpath('test_list_dir_null').mkdir()
        res = self.run(
            self.client.list_files,
            '/local/test_list_dir_null',
        )
        assert res.code == 200
        assert isinstance(res.data, ListItem)
        assert res.data.total == 0

    def test_get_item_info_dir(self):
        DATA_DIR.joinpath('test_ite_info_dir').mkdir()
        res = self.run(
            self.client.get_item_info,
            '/local/test_ite_info_dir'
        )
        assert res.code == 200
        assert isinstance(res.data, RawItem)

    def test_get_item_info_file(self):
        DATA_DIR.joinpath('test_ite_info_file.txt').write_text('abc')
        res = self.run(
            self.client.get_item_info,
            '/local/test_ite_info_file.txt'
        )
        assert res.code == 200
        assert isinstance(res, Resp)
        assert isinstance(res.data, RawItem)

    def test_get_dir(self):
        DATA_DIR.joinpath('test_ite_info_dir').mkdir()

        res = self.run(
            self.client.get_dir,
            '/local'
        )
        assert res.code == 200
        assert isinstance(res.data, list)
        assert isinstance(res.data[0], DirItem)

    def test_move(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = self.run(
            self.client.move,
            src_dir='/local/test_move_src',
            dst_dir='/local/test_move_dst',
            files=['test.txt']
        )

        assert res.code == 200
        assert DATA_DIR.joinpath('test_move_dst/test.txt').exists()
        assert not DATA_DIR.joinpath('test_move_src/test.txt').exists()

    def test_recursive_move(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test1.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_src/test2.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_src/test3.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = self.run(
            self.client.recursive_move,
            src_dir='/local/test_move_src',
            dst_dir='/local/test_move_dst',
        )

        assert res.code == 200
        assert DATA_DIR.joinpath('test_move_dst/test1.txt').exists()
        assert not DATA_DIR.joinpath('test_move_src/test1.txt').exists()

    def test_copy(self):
        DATA_DIR.joinpath('test_copy_src').mkdir()
        DATA_DIR.joinpath('test_copy_src/test.txt').write_text('abc')
        DATA_DIR.joinpath('test_copy_dst').mkdir()

        res = self.run(
            self.client.copy,
            src_dir='/local/test_copy_src',
            dst_dir='/local/test_copy_dst',
            files=['test.txt']
        )

        assert res.code == 200
        assert DATA_DIR.joinpath('test_copy_dst/test.txt').exists()
        assert DATA_DIR.joinpath('test_copy_src/test.txt').exists()

    def test_remove_file(self):
        DATA_DIR.joinpath('test_remove_file.txt').write_text('abc')
        res = self.run(
            self.client.remove,
            path='/local',
            names=['test_remove_file.txt']
        )
        assert res.code == 200
        assert not DATA_DIR.joinpath('test_remove_file.txt').exists()

    def test_remove_dir_has_file(self):
        DATA_DIR.joinpath('test_dir').mkdir()
        DATA_DIR.joinpath('test_dir/test1.txt').write_text('123')

        res = self.run(
            self.client.remove,
            path='/local',
            names=['test_dir']
        )
        assert res.code == 200
        assert not DATA_DIR.joinpath('test_dir/test1.txt').exists()
        assert not DATA_DIR.joinpath('test_dir').exists()

    @pytest.mark.skip
    def test_remove_empty_directory(self):
        DATA_DIR.joinpath('test_dir').mkdir()
        res = self.run(
            self.client.remove_empty_directory,
            path='/local/test_dir/'
        )

        assert res.code == 200
        assert not DATA_DIR.joinpath('test_dir').exists()

    @pytest.mark.skip
    def test_remove_empty_directory_not(self):
        DATA_DIR.joinpath('test_dir').mkdir()
        DATA_DIR.joinpath('test_dir/test.txt').write_text('123')

        res = self.run(
            self.client.remove_empty_directory,
            path='/local/test_dir/'
        )

        assert res.code == 200
        assert not DATA_DIR.joinpath('test_dir').exists()

    @pytest.mark.skip
    def test_add_aria2(self):
        res = self.run(
            self.client.add_aria2,
            "/local",
            [""]
        )
        assert res.code == 200

    @pytest.mark.skip
    def test_add_qbit(self):
        """"""
        res = self.run(self.client.add_qbit, "/local", [""])
        assert res.code == 200

    def test_task_done(self):
        """"""
        DATA_DIR.joinpath('test.txt').write_text('abc')

        res = self.run(
            self.client.copy,
            src_dir='/local',
            dst_dir='/local_dst',
            files=['test.txt']
        )

        assert res.code == 200, res.message

        res = self.run(
            self.client.task_done,
            'copy'
        )
        assert res.code == 200, res.message
        assert isinstance(res.data, list)
        assert isinstance(res.data[0], Task)


class TestAsyncClient(TestSyncClient):
    @property
    def client(self) -> AsyncClient:
        return AsyncClient('http://localhost:5244', username="admin", password="123456")

    def run(self, func, *args, **kwargs):
        print("--- type", type(func))
        return asyncio.run(func(*args, **kwargs))

    def test_async_client(self):
        assert isinstance(self.client, AsyncClient)
