import datetime
import logging
from pathlib import Path
from typing import Optional

from json import JSONDecodeError

from pydantic import BaseModel as _BaseModel, computed_field

from functools import wraps

logger = logging.getLogger('alist-sdk.fs.model')

__all__ = [
    "BaseModel", "Item", "RawItem", "ListItem",
    "DirItem", "SearchItem", "Searches", "Me",
    "Task", "Resp",
    "Verify", "verify", "AsyncVerify", "async_verify"
]


class BaseModel(_BaseModel):

    @computed_field()
    @property
    def full_name(self) -> str:
        return Path(self.parent).joinpath(self.name).as_posix()


class ListItem(_BaseModel):
    """列出的目录"""
    content: list['Item'] | None
    total: int  # 总数
    readme: str  # 用于渲染Readme
    header: Optional[str] = ''  # 用于渲染Header
    write: bool  # 是否可写
    provider: str
    parent: Optional[str] = ''


class Item(BaseModel):
    """文件对象"""
    name: str  # 文件名
    size: int  # 文件大小
    is_dir: bool  # 是否是目录
    hashinfo: Optional[str] = 'null'  # v3.29.0
    hash_info: Optional[None] = None  # v3.29.0
    modified: datetime.datetime  # 修改时间
    created: Optional[datetime.datetime]  # v3.29.0 创建时间
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


class Me(_BaseModel):
    """"""
    id: int
    username: str
    password: str | None
    base_path: str
    role: int
    disabled: bool
    permission: int
    sso_id: str | None
    otp: Optional[bool]


class Task(_BaseModel):
    """ »» id	string	false	none	id	none
        »» name	string	false	none	任务名	none
        »» state	string	false	none	任务完成状态	none
        »» status	string	false	none		none
        »» progress	integer	false	none	进度	none
        »» error	string	false	none	错误信息	none
    """
    id: str
    name: str
    state: int
    status: str
    progress: int
    error: str


class Resp(_BaseModel):
    code: int
    message: str
    # data: ListItem
    data: None | str | Me | list[DirItem] | ListItem | Searches | RawItem | list[Task]


class Verify:
    def __init__(self):
        self.locals: dict = {}
        # self.res: Response

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

    def acting(self, resp: Resp):
        """对Resp做额外的修饰"""
        return resp

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.locals, self.res = func(*args, **kwargs)
            try:
                res_dict = self.res.json()
                resp = Resp(**res_dict)
                return self.acting(resp)

            except JSONDecodeError:
                logger.warning("JsonDecodeError: [http_status: %d] ", self.res.status_code)
                return Resp(code=self.res.status_code, message="JsonDecodeError", data=None)

        return wrapper  # 返回函数


verify = Verify


class AsyncVerify(Verify):
    """"""

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            self.locals, self.res = await func(*args, **kwargs)
            try:
                res_dict = self.res.json()
                resp = Resp(**res_dict)
                return self.acting(resp)

            except JSONDecodeError:
                logger.warning("[Async]JsonDecodeError: [http_status: %d] ", self.res.status_code)
                return Resp(code=self.res.status_code, message="[Async]JsonDecodeError", data=None)

        return async_wrapper  # 返回函数


async_verify = AsyncVerify
