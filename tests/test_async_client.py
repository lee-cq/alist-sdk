import asyncio
from alist_sdk import AsyncClient
from pathlib import Path

from .test_client import TestSyncClient, clear_dir

DATA_DIR = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST = Path(__file__).parent.joinpath('alist/test_dir')
DATA_DIR_DST.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)



def setup_function() -> None:
    clear_dir(DATA_DIR)
    clear_dir(DATA_DIR_DST)
    DATA_DIR.mkdir(exist_ok=True)
    DATA_DIR_DST.mkdir(exist_ok=True)


class TestAsyncClient(TestSyncClient):
    @property
    def client(self) -> AsyncClient:
        return AsyncClient('http://localhost:5244', username="admin", password="123456")

    def run(self, func, *args, **kwargs):
        print("--- type",type(func))
        return asyncio.run(func(*args, **kwargs))

    def test_async_client(self):
        assert isinstance(self.client, AsyncClient)


