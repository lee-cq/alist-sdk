from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """用户模型"""
    id: Optional[int | None]
    username: str
    salt: Optional[str | None] = Field(alias='Salt')
    password: Optional[str | None]
    base_path: Optional[str | None]
    role: Optional[int | None]
    disable: Optional[bool]
    permission: Optional[int]
    sso_id: Optional[str]


class Meta(BaseModel):
    """元数据   """
    id: int
    path: str
    password: str
    p_sub: bool
    write: bool
    w_sub: bool
    hide: str
    h_sub: bool
    readme: str
    r_sub: str
