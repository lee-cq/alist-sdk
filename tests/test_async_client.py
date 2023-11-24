import unittest
from pathlib import Path

import pytest
# import pytest_asyncio

from alist_sdk import *
from .test_client import clear_dir, create_storage_local

client = Client('http://localhost:5244', username='admin', password='123456')
async_client = AsyncClient('http://localhost:5244', verify=False)

DATA_DIR = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


def setup_module():
    async_client.headers.update(client.headers)


def setup_function():
    create_storage_local(client, 'local', DATA_DIR)
    create_storage_local(client, 'local_dst', DATA_DIR_DST)


def teardown_function() -> None:
    clear_dir(DATA_DIR)
    clear_dir(DATA_DIR_DST)
    DATA_DIR.mkdir(exist_ok=True)
    DATA_DIR_DST.mkdir(exist_ok=True)


@pytest.mark.asyncio
async def test_login():
    _client = AsyncClient("http://localhost:5244", verify=False)
    await _client.login(username='admin', password="123456", )
    res = await _client.me()
    assert res.code == 200
    assert isinstance(res.data, Me)
    assert res.data.username == 'admin'
    print('OK')


@pytest.mark.asyncio
async def test_mkdir():
    res = await async_client.mkdir('/local/test_mkdir')
    assert res.code == 200
    assert DATA_DIR.joinpath('test_mkdir').exists(), "创建失败"


@pytest.mark.asyncio
async def test_rename():
    DATA_DIR.joinpath('test_mkdir').mkdir()
    if DATA_DIR.joinpath('test_rename').exists():
        DATA_DIR.joinpath('test_rename').rmdir()
    res = await async_client.rename('test_rename', '/local/test_mkdir')
    assert res.data is None
    assert res.code == 200
    assert DATA_DIR.joinpath('test_rename').exists()
    assert DATA_DIR.joinpath('test_mkdir').exists()


@pytest.mark.skip
@pytest.mark.asyncio
async def test_upload_file_from_data():
    data = b"test_data"
    alist_full_name = '/local/upload_file_form_data'
    path_file = DATA_DIR.joinpath('upload_file_form_data')
    res = await async_client.upload_file_form_data(data, alist_full_name, as_task=False)
    assert res.message is None
    assert res.code == 200
    assert path_file.exists()


@pytest.mark.asyncio
async def test_upload_put():
    alist_full_name = '/local/upload_file_form_data'
    alist_data_path = DATA_DIR.joinpath('upload_file_form_data')
    res = await async_client.upload_file_put(__file__, alist_full_name, as_task=False)
    assert res.data is None
    assert res.code == 200
    assert alist_data_path.exists()


@pytest.mark.asyncio
async def test_list_dir():
    DATA_DIR.joinpath('test_list_dir_dir').mkdir()
    DATA_DIR.joinpath('test_list_dir_file').write_text('test')
    res = await async_client.list_files('/local', )
    assert res.code == 200
    assert isinstance(res.data, ListItem)
    assert isinstance(res.data.content[0], Item)


@pytest.mark.asyncio
async def test_list_dir_null():
    DATA_DIR.joinpath('test_list_dir_null').mkdir()
    res = await async_client.list_files('/local/test_list_dir_null', )
    assert res.code == 200
    assert isinstance(res.data, ListItem)
    assert res.data.total == 0


@pytest.mark.asyncio
async def test_get_item_info_dir():
    DATA_DIR.joinpath('test_ite_info_dir').mkdir()
    res = await async_client.get_item_info('/local/test_ite_info_dir')
    assert res.code == 200
    assert isinstance(res.data, RawItem)


@pytest.mark.asyncio
async def test_get_item_info_file():
    DATA_DIR.joinpath('test_ite_info_file.txt').write_text('abc')
    res = await async_client.get_item_info('/local/test_ite_info_file.txt')
    assert res.code == 200
    assert isinstance(res, Resp)
    assert isinstance(res.data, RawItem)


@pytest.mark.asyncio
async def test_get_dir():
    DATA_DIR.joinpath('test_ite_info_dir').mkdir()
    res = await async_client.get_dir('/local')
    assert res.code == 200
    assert isinstance(res.data, list)
    assert isinstance(res.data[0], DirItem)


@pytest.mark.asyncio
async def test_move():
    DATA_DIR.joinpath('test_move_src').mkdir()
    DATA_DIR.joinpath('test_move_src/test.txt').write_text('abc')
    DATA_DIR.joinpath('test_move_dst').mkdir()

    res = await async_client.move(src_dir='/local/test_move_src',
                                  dst_dir='/local/test_move_dst',
                                  files=['test.txt']
                                  )

    assert res.code == 200
    assert DATA_DIR.joinpath('test_move_dst/test.txt').exists()
    assert not DATA_DIR.joinpath('test_move_src/test.txt').exists()


@pytest.mark.asyncio
async def test_recursive_move():
    DATA_DIR.joinpath('test_move_src').mkdir()
    DATA_DIR.joinpath('test_move_src/test1.txt').write_text('abc')
    DATA_DIR.joinpath('test_move_src/test2.txt').write_text('abc')
    DATA_DIR.joinpath('test_move_src/test3.txt').write_text('abc')
    DATA_DIR.joinpath('test_move_dst').mkdir()

    res = await async_client.recursive_move(src_dir='/local/test_move_src',
                                            dst_dir='/local/test_move_dst',
                                            )

    assert res.code == 200
    assert DATA_DIR.joinpath('test_move_dst/test1.txt').exists()
    assert not DATA_DIR.joinpath('test_move_src/test1.txt').exists()


@pytest.mark.asyncio
async def test_copy():
    DATA_DIR.joinpath('test_move_src').mkdir()
    DATA_DIR.joinpath('test_move_src/test.txt').write_text('abc')
    DATA_DIR.joinpath('test_move_dst').mkdir()

    res = await async_client.copy(src_dir='/local/test_move_src',
                                  dst_dir='/local/test_move_dst',
                                  files=['test.txt']
                                  )

    assert res.code == 200
    assert DATA_DIR.joinpath('test_move_dst/test.txt').exists()
    assert DATA_DIR.joinpath('test_move_src/test.txt').exists()


@pytest.mark.asyncio
async def test_remove_file():
    DATA_DIR.joinpath('test_remove_file.txt').write_text('abc')
    res = await async_client.remove(path='/local',
                                    names=['test_remove_file.txt']
                                    )
    assert res.code == 200
    assert not DATA_DIR.joinpath('test_remove_file.txt').exists()


@pytest.mark.asyncio
async def test_remove_dir_has_file():
    DATA_DIR.joinpath('test_dir').mkdir()
    DATA_DIR.joinpath('test_dir/test1.txt').write_text('123')

    res = await async_client.remove(path='/local', names=['test_dir'])
    assert res.code == 200
    assert not DATA_DIR.joinpath('test_dir/test1.txt').exists()
    assert not DATA_DIR.joinpath('test_dir').exists()


@pytest.mark.asyncio
@unittest.expectedFailure
async def test_remove_empty_directory():
    DATA_DIR.joinpath('test_dir').mkdir()
    res = await async_client.remove_empty_directory(path='/local/test_dir/')

    assert res.code == 200
    assert not DATA_DIR.joinpath('test_dir').exists()


@unittest.expectedFailure
@pytest.mark.asyncio
async def test_remove_empty_directory_not():
    DATA_DIR.joinpath('test_dir').mkdir()
    DATA_DIR.joinpath('test_dir/test.txt').write_text('123')

    res = await async_client.remove_empty_directory(path='/local/test_dir/')

    assert res.code == 200
    assert not DATA_DIR.joinpath('test_dir').exists()


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_add_aria2():
    res = await async_client.add_aria2("/local", [""])
    assert res.code == 200


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_add_qbit():
    """"""
    res = await async_client.add_qbit("/local", [""])
    assert res.code == 200


# ==========================
@pytest.mark.asyncio
async def test_task_done():
    """"""
    DATA_DIR.joinpath('test.txt').write_text('abc')

    res = await async_client.copy(src_dir='/local',
                                  dst_dir='/local_dst',
                                  files=['test.txt']
                                  )

    assert res.code == 200, res.message

    res = await async_client.task_done('copy')
    assert res.code == 200, res.message
    assert isinstance(res.data, list)
    assert isinstance(res.data[0], Task)
