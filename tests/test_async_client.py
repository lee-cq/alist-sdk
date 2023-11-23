import asyncio
import unittest
from pathlib import Path

import pytest
import pytest_asyncio

from alist_sdk import *
from .test_client import clear_dir, create_storage_local

client = Client('http://localhost:5244', username='admin', password='123456')
async_client = AsyncClient('http://localhost:5244', verify=False)

DATA_DIR = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)



@pytest.mark.asyncio
async def setup_module():
    print("setup ...")
    await async_client.login(username='admin', password='123456')


@pytest.mark.asyncio
async def test_login():
    _client = AsyncClient("http://localhost:5244", verify=False)
    await _client.login(username='admin', password="123456", )
    res = await _client.me()
    assert res.code == 200
    assert isinstance(res.data, Me)
    assert res.data.username == 'admin'


# @pytest.mark.asyncio
# async def test_me():

#     res = await async_client.me()
#     assert res.code == 200
#     assert isinstance(res.data, Me)
#     assert res.data.username == 'admin'


class FSTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        create_storage_local(client, 'local', DATA_DIR)

    def tearDown(self) -> None:
        clear_dir(DATA_DIR)
        DATA_DIR.mkdir(exist_ok=True)

    async def test_mkdir(self):
        res = await async_client.mkdir('/local/test_mkdir')
        self.assertEqual(res.data, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_mkdir').exists(), "创建失败")

    async def test_rename(self):
        DATA_DIR.joinpath('test_mkdir').mkdir()
        if DATA_DIR.joinpath('test_rename').exists():
            DATA_DIR.joinpath('test_rename').rmdir()
        res = await async_client.rename('test_rename', '/local/test_mkdir')
        self.assertEqual(res.data, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_rename').exists())
        self.assertFalse(DATA_DIR.joinpath('test_mkdir').exists())

    @unittest.SkipTest
    async def test_upload_file_from_data(self):
        data = b"test_data"
        alist_full_name = '/local/upload_file_form_data'
        path_file = DATA_DIR.joinpath('upload_file_form_data')
        res = await async_client.upload_file_form_data(data, alist_full_name, as_task=False)
        self.assertEqual(res, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(path_file.exists())

    async def test_upload_put(self):
        alist_full_name = '/local/upload_file_form_data'
        alist_data_path = DATA_DIR.joinpath('upload_file_form_data')
        res = await async_client.upload_file_put(__file__, alist_full_name, as_task=False)
        self.assertEqual(res.data, None)
        self.assertEqual(res.code, 200)
        self.assertTrue(alist_data_path)

    async def test_list_dir(self):
        DATA_DIR.joinpath('test_list_dir_dir').mkdir()
        DATA_DIR.joinpath('test_list_dir_file').write_text('test')
        res = await async_client.list_files('/local', )
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, ListItem)
        self.assertIsInstance(res.data.content[0], Item)

    async def test_list_dir_null(self):
        DATA_DIR.joinpath('test_list_dir_null').mkdir()
        res = await async_client.list_files('/local/test_list_dir_null', )
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, ListItem)
        self.assertEqual(res.data.total, 0)

    async def test_get_item_info_dir(self):
        DATA_DIR.joinpath('test_ite_info_dir').mkdir()
        res = await async_client.get_item_info('/local/test_ite_info_dir')
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, RawItem)

    async def test_get_item_info_file(self):
        DATA_DIR.joinpath('test_ite_info_file.txt').write_text('abc')
        res = await async_client.get_item_info('/local/test_ite_info_file.txt')
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res, Resp)
        self.assertIsInstance(res.data, RawItem)

    async def test_get_dir(self):
        DATA_DIR.joinpath('test_ite_info_dir').mkdir()
        raise

        res = await async_client.get_dir('/local')
        self.assertEqual(res.code, 200)
        self.assertIsInstance(res.data, list)
        self.assertIsInstance(res.data[0], DirItem)

    async def test_move(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = await async_client.move(src_dir='/local/test_move_src',
                                      dst_dir='/local/test_move_dst',
                                      files=['test.txt']
                                      )

        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_move_dst/test.txt').exists())
        self.assertFalse(DATA_DIR.joinpath('test_move_src/test.txt').exists())

    async def test_recursive_move(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test1.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_src/test2.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_src/test3.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = await async_client.recursive_move(src_dir='/local/test_move_src',
                                                dst_dir='/local/test_move_dst',
                                                )

        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_move_dst/test1.txt').exists())
        self.assertFalse(DATA_DIR.joinpath('test_move_src/test1.txt').exists())

    async def test_copy(self):
        DATA_DIR.joinpath('test_move_src').mkdir()
        DATA_DIR.joinpath('test_move_src/test.txt').write_text('abc')
        DATA_DIR.joinpath('test_move_dst').mkdir()

        res = await async_client.copy(src_dir='/local/test_move_src',
                                      dst_dir='/local/test_move_dst',
                                      files=['test.txt']
                                      )

        self.assertEqual(res.code, 200)
        self.assertTrue(DATA_DIR.joinpath('test_move_dst/test.txt').exists())
        self.assertTrue(DATA_DIR.joinpath('test_move_src/test.txt').exists())

    async def test_remove_file(self):
        DATA_DIR.joinpath('test_remove_file.txt').write_text('abc')
        res = await async_client.remove(path='/local',
                                        names=['test_remove_file.txt']
                                        )
        self.assertEqual(res.code, 200)
        self.assertFalse(DATA_DIR.joinpath('test_remove_file.txt').exists())

    async def test_remove_dir_has_file(self):
        DATA_DIR.joinpath('test_dir').mkdir()
        DATA_DIR.joinpath('test_dir/test1.txt').write_text('123')

        res = await async_client.remove(path='/local',
                                        names=['test_dir']
                                        )
        self.assertEqual(res.code, 200)
        self.assertFalse(DATA_DIR.joinpath('test_dir/test1.txt').exists())
        self.assertFalse(DATA_DIR.joinpath('test_dir').exists())

    # @unittest.expectedFailure
    # async def test_remove_empty_directory(self):
    #     DATA_DIR.joinpath('test_dir').mkdir()
    #     res = await async_client.remove_empty_directory(path='/local/test_dir/')

    #     self.assertEqual(res.code, 200)
    #     self.assertFalse(DATA_DIR.joinpath('test_dir').exists())

    # @unittest.expectedFailure
    # async def test_remove_empty_directory_not(self):
    #     DATA_DIR.joinpath('test_dir').mkdir()
    #     DATA_DIR.joinpath('test_dir/test.txt').write_text('123')

    #     res = await async_client.remove_empty_directory(path='/local/test_dir/')

    #     self.assertEqual(res.code, 200)
    #     self.assertFalse(DATA_DIR.joinpath('test_dir').exists())

    # @unittest.expectedFailure
    # async def test_add_aria2(self):
    #     res = await async_client.add_aria2("/local", [""])
    #     self.assertEqual(res.code, 200)

    # @unittest.expectedFailure
    # async def test_add_qbit(self):
    #     """"""
    #     res = await async_client.add_qbit("/local", [""])
    #     self.assertEqual(res.code, 200)


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

    async def test_task_done(self):
        """"""
        DATA_DIR.joinpath('test.txt').write_text('abc')

        res = await async_client.copy(src_dir='/local',
                                      dst_dir='/local_dst',
                                      files=['test.txt']
                                      )

        self.assertEqual(res.code, 200, res.message)

        res = await async_client.task_done('copy')
        self.assertEqual(res.code, 200, res.message)
        self.assertIsInstance(res.data, list)
        self.assertIsInstance(res.data[0], Task)


if __name__ == '__main__':
    pass
