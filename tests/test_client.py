import os
import unittest
from pathlib import Path

from alist_sdk import *

client = Client('http://localhost:5244', username='admin', password='123456')
DATA_DIR = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST = Path(__file__).parent.joinpath('alist/test_dir')
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
    if f'/{mount_name}' not in [i['mount_path'] for i in client.get("/api/admin/storage/list").json()['data']['content']]:
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


class BaseTestCase(unittest.TestCase):

    def test_login(self):
        _client = Client("http://localhost:5244", verify=False)
        self.assertTrue(_client.login(username='admin', password="123456", ), "登陆失败")

    def test_me(self):
        res = client.me()
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, Me, "数据结构错误。")


class FSTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        create_storage_local(client, 'local', DATA_DIR)

    def tearDown(self) -> None:
        clear_dir(DATA_DIR)
        DATA_DIR.mkdir(exist_ok=True)

    def test_mkdir(self):
        res = client.mkdir('/local/test_mkdir')
        self.assertEqual(res.data, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_mkdir').exists(), "创建失败")

    def test_rename(self):
        DATA_DIR.joinpath('test_mkdir').mkdir()
        if DATA_DIR.joinpath('test_rename').exists():
            DATA_DIR.joinpath('test_rename').rmdir()
        res = client.rename('test_rename', '/local/test_mkdir')
        self.assertEqual(res.data, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_rename').exists())
        self.assertFalse(DATA_DIR.joinpath('test_mkdir').exists())

    @unittest.SkipTest
    def test_upload_file_from_data(self):
        data = b"test_data"
        alist_full_name = '/local/upload_file_form_data'
        path_file = DATA_DIR.joinpath('upload_file_form_data')
        res = client.upload_file_form_data(data, alist_full_name, as_task=False)
        self.assertEqual(res, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(path_file.exists())

    def test_upload_put(self):
        alist_full_name = '/local/upload_file_form_data'
        alist_data_path = DATA_DIR.joinpath('upload_file_form_data')
        res = client.upload_file_put(__file__, alist_full_name, as_task=False)
        self.assertEqual(res.data, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(alist_data_path)

    def test_list_dir(self):
        DATA_DIR.joinpath('test_list_dir_dir').mkdir()
        DATA_DIR.joinpath('test_list_dir_file').write_text('test')
        res = client.list_files('/local', )
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, ListItem)
        self.assertIsInstance(res.data.content[0], Item)

    def test_list_dir_null(self):
        DATA_DIR.joinpath('test_list_dir_null').mkdir()
        res = client.list_files('/local/test_list_dir_null', )
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, ListItem)
        self.assertEqual(res.data.total, 0)

    def test_get_item_info_dir(self):
        DATA_DIR.joinpath('test_ite_info_dir').mkdir()
        res = client.get_item_info('/local/test_ite_info_dir')
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, RawItem)

    def test_get_item_info_file(self):
        DATA_DIR.joinpath('test_ite_info_file.txt').write_text('abc')
        res = client.get_item_info('/local/test_ite_info_file.txt')
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res, Resp)
        self.assertIsInstance(res.data, RawItem)

    def test_get_dir(self):
        DATA_DIR.joinpath('test_ite_info_dir').mkdir()

        res = client.get_dir('/local')
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, list)
        self.assertIsInstance(res.data[0], DirItem)

    def test_move(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = client.move(src_dir='/local/test_move_src',
                          dst_dir='/local/test_move_dst',
                          files=['test.txt']
                          )

        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_move_dst/test.txt').exists())
        self.assertFalse(DATA_DIR.joinpath('test_move_src/test.txt').exists())

    def test_recursive_move(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test1.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_src/test2.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_src/test3.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = client.recursive_move(src_dir='/local/test_move_src',
                                    dst_dir='/local/test_move_dst',
                                    )

        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_move_dst/test1.txt').exists())
        self.assertFalse(DATA_DIR.joinpath('test_move_src/test1.txt').exists())

    def test_copy(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = client.copy(src_dir='/local/test_move_src',
                          dst_dir='/local/test_move_dst',
                          files=['test.txt']
                          )

        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_move_dst/test.txt').exists())
        self.assertTrue(DATA_DIR.joinpath('test_move_src/test.txt').exists())

    def test_remove_file(self):
        DATA_DIR.joinpath('test_remove_file.txt').write_text('abc')
        res = client.remove(path='/local',
                            names=['test_remove_file.txt']
                            )
        self.assertEqual(res.code, 200)
        self.assertFalse(DATA_DIR.joinpath('test_remove_file.txt').exists())

    def test_remove_dir_has_file(self):
        DATA_DIR.joinpath('test_dir').mkdir()
        DATA_DIR.joinpath('test_dir/test1.txt').write_text('123')

        res = client.remove(path='/local',
                            names=['test_dir']
                            )
        self.assertEqual(res.code, 200)
        self.assertFalse(DATA_DIR.joinpath('test_dir/test1.txt').exists())
        self.assertFalse(DATA_DIR.joinpath('test_dir').exists())

    @unittest.expectedFailure
    def test_remove_empty_directory(self):
        DATA_DIR.joinpath('test_dir').mkdir()
        res = client.remove_empty_directory(path='/local/test_dir/')

        self.assertEqual(res.code, 200)
        self.assertFalse(DATA_DIR.joinpath('test_dir').exists())

    @unittest.expectedFailure
    def test_remove_empty_directory_not(self):
        DATA_DIR.joinpath('test_dir').mkdir()
        DATA_DIR.joinpath('test_dir/test.txt').write_text('123')

        res = client.remove_empty_directory(path='/local/test_dir/')

        self.assertEqual(res.code, 200)
        self.assertFalse(DATA_DIR.joinpath('test_dir').exists())

    @unittest.expectedFailure
    def test_add_aria2(self):
        res = client.add_aria2("/local", [""])
        self.assertEqual(res.code, 200)

    @unittest.expectedFailure
    def test_add_qbit(self):
        """"""
        res = client.add_qbit("/local", [""])
        self.assertEqual(res.code, 200)


class AdminTaskTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        create_storage_local(client, 'local', DATA_DIR)
        create_storage_local(client, 'local_dst', DATA_DIR_DST)

    def setUp(self) -> None:
        clear_dir(DATA_DIR)
        clear_dir(DATA_DIR_DST)
        DATA_DIR.mkdir(exist_ok=True)
        DATA_DIR_DST.mkdir(exist_ok=True)

    def test_task_done(self):
        """"""
        DATA_DIR.joinpath('test.txt').write_text('abc')

        res = client.copy(src_dir='/local',
                          dst_dir='/local_dst',
                          files=['test.txt']
                          )

        self.assertEqual(res.code, 200, res.message)

        res = client.task_done('copy')
        self.assertEqual(res.code, 200, res.message)
        self.assertIsInstance(res.data, list)
        self.assertIsInstance(res.data[0], Task)




if __name__ == '__main__':
    unittest.main()
