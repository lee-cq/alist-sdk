import datetime
import logging
import os
from pathlib import PurePosixPath
from typing import Optional, Literal

from pydantic import (
    BaseModel as _BaseModel,
    computed_field,
    field_serializer,
)

logger = logging.getLogger("alist-sdk.fs.model")

__all__ = [
    "SearchScopeModify",
    "TaskType",
    "TaskTypeModify",
    "TaskStateModify",
    "TaskStatusModify",
    "OrderDirectionModify",
    "OrderByModify",
    "ExtractFolderModify",
    "BaseModel",
    "Item",
    "RawItem",
    "ListItem",
    "DirItem",
    "SearchItem",
    "Me",
    "Task",
    "ListTask",
    "AsTask",
    "Resp",
    "HashInfo",
    "NoneType",
    "ListContents",
    "User",
    "Storage",
    "Meta",
    "Setting",
]

NoneType = type(None)

SearchScopeModify = Literal[0, 1, 2]  # 0-全部 1-文件夹 2-文件

TaskType = [
    "copy",
    "upload",
    "offline_download",
    "offline_download_transfer",
]
TaskTypeModify = Literal[
    "copy",
    "upload",
    "offline_download",
    "offline_download_transfer",
]
# 0- 等待 1- 正在运行 2- 成功 3- 失败 4- 获取源对象 5- 上传中  7- 已取消 8- 重试中
TaskStateModify = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]
TaskStatusModify = Literal[
    "",
    "waiting",
    "running",
    "success",
    "failed",
    "getting src object",
    "uploading",
]

OrderDirectionModify = Literal["", "asc", "desc"]
OrderByModify = Literal["", "size", "name"]
ExtractFolderModify = Literal["", "front", "back", "none"]


class BaseModel(_BaseModel):
    parent: Optional[str | PurePosixPath | None] = ""

    @computed_field()
    @property
    def full_name(self) -> PurePosixPath:
        return PurePosixPath(self.parent).joinpath(self.name)

    @field_serializer("full_name", mode="wrap")
    def serializer_path(self, value: PurePosixPath, _) -> str:
        return value.as_posix()


class ListItem(_BaseModel):
    """列出的目录"""

    content: list["Item"] | None
    total: int  # 总数
    readme: str  # 用于渲染Readme
    header: Optional[str] = ""  # 用于渲染Header
    write: bool  # 是否可写
    provider: str


class HashInfo(_BaseModel):
    """Hash 信息"""

    md5: Optional[str] = None
    sha1: Optional[str] = None


class Item(BaseModel):
    """文件对象"""

    name: str  # 文件名
    size: int  # 文件大小
    is_dir: bool  # 是否是目录
    hashinfo: Optional[str] = "null"  # v3.29.0
    hash_info: Optional[HashInfo | None] = None  # v3.29.0
    modified: datetime.datetime  # 修改时间
    created: Optional[datetime.datetime] = None  # v3.29.0 创建时间
    sign: str  # 签名
    thumb: str  # 缩略图
    type: int  # 类型


class RawItem(Item):
    """一个对象的全部信息"""

    raw_url: str = ""
    readme: str = ""
    provider: str = ""
    related: str | None | list["RawItem"] = None


class SearchItem(BaseModel):
    parent: str
    name: str
    is_dir: bool
    size: int
    type: int


class DirItem(BaseModel):
    name: str
    modified: datetime.datetime


class Me(_BaseModel):
    """
    /api/me
    """

    id: int
    username: str
    password: str | None
    base_path: str
    role: int
    disabled: bool
    permission: int
    sso_id: str | None
    otp: Optional[bool] = False


class Task(_BaseModel):
    """
    »» id	string	false	none	id	none
    »» name	string	false	none	任务名	none
    »» state	string	false	none	任务完成状态	none
    »» status	string	false	none		none
    »» progress	integer	false	none	进度	none
    »» error	string	false	none	错误信息	none
    {
    "id":"0Vdzdi3BO_8vYujh72OTu",
    "name":"copy [/local](/test.txt) to [/local_dst](/)",
    "state":0,
    "status":"",
    "progress":0,
    "error":""
    }
    """

    id: str  # 任务ID
    name: str  # 任务名
    state: TaskStateModify  # 任务完成状态
    status: TaskStatusModify  # 任务状态
    progress: int | float  # 进度
    error: str  # 错误信息


class AsTask(_BaseModel):
    """/api/fs/put .headers"""

    task: Task


class ListTask(_BaseModel):
    tasks: list[Task]


class ID(_BaseModel):
    id: int | str | None


class Setting(_BaseModel):
    """/api/admin/setting/list .data.[]"""

    key: str
    value: str
    help: str  # 帮助信息
    type: str  # TODO 类型指导
    options: str
    group: int
    flag: int


class Storage(_BaseModel):
    # /api/admin/storage/list .data.content.[]
    # ListContent.content[Storage]
    id: Optional[int] = None
    mount_path: str | os.PathLike
    order: int
    driver: str
    cache_expiration: int
    status: str
    addition: str  # TODO JSON
    remark: str = ""
    modified: datetime.datetime
    disabled: bool
    enable_sign: bool
    order_by: OrderByModify
    order_direction: OrderDirectionModify
    extract_folder: ExtractFolderModify  # 提取文件夹位置
    web_proxy: bool
    webdav_policy: str  # webdav策略
    down_proxy_url: str = ""


class User(_BaseModel):
    """/api/admin/user/list .data.content.[]"""

    id: int
    username: str
    password: str
    base_path: PurePosixPath = PurePosixPath("/")
    role: int  #
    disabled: bool
    permission: int
    sso_id: str


class Meta(_BaseModel):
    """/api/admin/meta/list .data.content.[]"""

    id: int
    path: PurePosixPath
    password: str
    p_sub: bool
    write: bool
    w_sub: bool
    hide: str
    h_sub: bool
    readme: str
    r_sub: bool
    header: str
    header_sub: bool


class ListContents(_BaseModel):
    content: list[SearchItem | Storage | User | Meta] | None
    total: int


class Resp(_BaseModel):
    code: int
    message: str
    # data: ListTask
    data: (
        None
        | str
        | Me
        | list[DirItem]
        | list[Setting]
        | ListItem
        | ListContents
        | RawItem
        | ListTask
        | list[Task]
        | AsTask
        | ID
    )
