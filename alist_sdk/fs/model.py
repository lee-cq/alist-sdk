import datetime
import logging
from pathlib import Path
from typing import Optional

from httpx import Response
from json import JSONDecodeError

from pydantic import BaseModel as _BaseModel, computed_field
from ..client import Client

from functools import wraps

logger = logging.getLogger('alist-sdk.fs.model')

__all__ = [
    "BaseFS", "BaseModel",
    "Item", "RawItem", "ListItem",
    "DirItem", "SearchItem", "Searches",
    "Resp", "Verify", "verify"
]


class BaseFS:
    def __init__(self, client: Client):
        self.client = client


class BaseModel(_BaseModel):

    @computed_field()
    def full_name(self) -> str:
        return Path(self.parent).joinpath(self.name).as_posix()


class ListItem(BaseModel):
    """列出的目录"""
    content: list['Item'] | None
    total: int  # 总数
    readme: str  # 用于渲染Readme
    write: bool  # 是否可写
    provider: str
    parent: Optional[str] = ''


class Item(BaseModel):
    """文件对象"""
    name: str  # 文件名
    size: int  # 文件大小
    is_dir: bool  # 是否是目录
    modified: datetime.datetime  # 修改时间
    sign: str  # 签名
    thumb: str  # 缩略图
    type: int  # 类型
    parent: Optional[str] = ''


class RawItem(BaseModel):
    """一个对象的全部信息"""
    name: str
    size: int
    is_dir: bool
    modified: datetime.datetime
    sign: str
    thumb: str
    type: int
    raw_url: str
    readme: str
    provider: str
    related: str | None
    parent: Optional[str] = ''


class SearchItem(BaseModel):
    """
    "parent": "/m",
        "name": "4305da1e",
        "is_dir": false,
        "size": 393090,
        "type": 0
    """
    parent: str
    name: str
    is_dir: bool
    size: int
    type: int


class Searches(_BaseModel):
    content: list[SearchItem] | None
    total: int


class DirItem(BaseModel):
    name: str
    modified: datetime.datetime
    parent: Optional[str] | None = ''


class Resp(_BaseModel):
    code: int
    message: str
    data: None | list[DirItem] | ListItem | Searches | RawItem


class Verify:
    def __init__(self):
        self.locals: dict = {}

    def add_parent(self, res_dict: dict):
        res_dict.setdefault('parent', self.locals.get('path'))

    @property
    def ex_action(self):
        """"""
        return {
            ListItem: [self.add_parent],
            Item: [self.add_parent],
            RawItem: [self.add_parent],
            dict: [],
            BaseModel: []
        }

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.locals, res = func(*args, **kwargs)
            res: Response
            try:
                res_dict = res.json()
                return Resp(**res_dict)

            except JSONDecodeError:
                logger.warning("JsonDecodeError: [http_status: %d] ", res.status_code)
                return Resp(code=res.status_code, message="JsonDecodeError", data=None)

        return wrapper  # 返回函数


verify = Verify