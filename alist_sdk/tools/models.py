from pydantic import BaseModel
from alist_sdk.models import Storage, Setting, User, Meta


class Configs(BaseModel):
    settings: list[Setting] = []
    users: list[User] = []
    storages: list[Storage] = []
    metas: list[Meta] = []
