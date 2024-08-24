import json
import logging
from functools import wraps
from json import JSONDecodeError

import httpx
from pydantic import ValidationError

from alist_sdk.models import Resp, ListItem, Item, RawItem, BaseModel, TaskType

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
        self.request: httpx.Request | None = None

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

    def acting(self, resp: Resp) -> Resp:
        """对Resp做额外的修饰"""
        if not isinstance(self.request, httpx.Request):
            return resp

        if (
            self.request.url.path
            in [
                *[
                    f"/api/admin/task/{tt}/{ts}"
                    for tt in TaskType
                    for ts in ["done", "undone"]
                ],
                "/user/info",
            ]
            and resp.code == 200
        ):
            resp.data = resp.data or []

        return resp

    def _verify(self, local_s, res: httpx.Response):
        self.locals.update(local_s)
        self.request = res.request
        url = res.request.url.path
        args = "\n>>>".join(f"{k}: {v}" for k, v in self.locals.items() if k != "data")
        logger.debug(
            f">>> 响应详情: [{self.request.method}] {url}\n"
            f">>> {args}\n"
            f"<<<[{res.status_code}]\n"
            f"<<<{res.text}"
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
                f"{json.dumps(res.json(), indent=2, ensure_ascii=False)} \n"
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
