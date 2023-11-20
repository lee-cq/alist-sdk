import datetime

from pydantic import BaseModel
from ..client import Client


class BaseFS:
    def __init__(self, client: Client):
        self.client = client


class Dir(BaseModel):
    """列出的目录"""
    content: list['Item']
    total: int  # 总数
    readme: str  # 用于渲染Readme
    write: bool  # 是否可写
    provider: str


class Item(BaseModel):
    """文件对象"""
    name: str  # 文件名
    size: int  # 文件大小
    is_dir: bool  # 是否是目录
    modified: datetime.datetime  # 修改时间
    sign: str  # 签名
    thumb: str  # 缩略图
    type: str  # 类型


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
    related: str
