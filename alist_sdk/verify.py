import json
import logging
from functools import wraps
from json import JSONDecodeError

from alist_sdk.models import Resp, ListItem, Item, RawItem, BaseModel

logger = logging.getLogger('alist-sdk.verify')

__all__ = [
    "Verify",
    "verify",
    "AsyncVerify",
    "async_verify",
]


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
            logger.debug(
                f"收到响应: [{self.res.status_code}]\n "
                f"{json.dumps(self.res.json(), indent=2, ensure_ascii=False)}"
            )
            try:
                res_dict = self.res.json()
                resp = Resp(**res_dict)
                return self.acting(resp)

            except JSONDecodeError:
                logger.warning(
                    "JsonDecodeError: [http_status: %d] ", self.res.status_code)
                return Resp(code=self.res.status_code, message="JsonDecodeError",
                            data=None)

        return wrapper  # 返回函数


verify = Verify


class AsyncVerify(Verify):
    """"""

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Resp:
            self.locals, self.res = await func(*args, **kwargs)
            logger.debug(
                f"收到响应: [{self.res.status_code}]\n "
                f"{json.dumps(self.res.text, indent=2, ensure_ascii=False)}"
            )
            try:
                res_dict = self.res.json()
                resp = Resp(**res_dict)
                return self.acting(resp)

            except JSONDecodeError:
                logger.warning(
                    "[Async]JsonDecodeError: [http_status: %d] ", self.res.status_code)
                return Resp(code=self.res.status_code, message="[Async]JsonDecodeError",
                            data=None)

        return async_wrapper  # 返回函数


async_verify = AsyncVerify
