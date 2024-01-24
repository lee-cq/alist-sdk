import json
import logging
from functools import wraps
from json import JSONDecodeError

import httpx
from pydantic import ValidationError

from alist_sdk.models import Resp, ListItem, Item, RawItem, BaseModel

logger = logging.getLogger("alist-sdk.verify")

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
        res_dict.setdefault("parent", self.locals.get("path"))

    @property
    def ex_action(self):
        """"""
        return {
            ListItem: [self.add_parent],
            Item: [self.add_parent],
            RawItem: [self.add_parent],
            dict: [],
            BaseModel: [],
        }

    def acting(self, resp: Resp):
        """对Resp做额外的修饰"""
        return resp

    def _verify(self, local_s, res: httpx.Response):
        _ = local_s
        url = res.request.url.path
        logger.debug(
            f"收到响应: {url}[{res.status_code}]\n "
            f"{json.dumps(res.text, indent=2, ensure_ascii=False)}"
        )
        try:
            res_dict = res.json()
            resp = Resp.model_validate(res_dict)
            return self.acting(resp)

        except JSONDecodeError:
            logger.warning("JsonDecodeError: [http_status: %d] ", res.status_code)
            return Resp(
                code=res.status_code, message=f"JsonDecodeError: {res.text}", data=None
            )

        except ValidationError as _e:
            req_headers = "\n>>> ".join(
                f"{k}: {v}" for k, v in res.request.headers.items()
            )
            res_headers = "\n<<< ".join(f"{k}: {v}" for k, v in res.headers.items())
            logger.error(
                f"RESP验证错误：\n"
                f">>> {res.request.method} {res.request.url}"
                f">>> {req_headers}\n\n"
                f">>> {local_s = }\n"
                f"========= Request End =========\n"
                f"<<< {res_headers}\n\n"
                f"{res.text} \n"
                f"========= Resp End =========",
            )
            raise _e

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._verify(*func(*args, **kwargs))

        return wrapper  # 返回函数


verify = Verify


class AsyncVerify(Verify):
    """"""

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Resp:
            return self._verify(*(await func(*args, **kwargs)))

        return async_wrapper  # 返回函数


async_verify = AsyncVerify
