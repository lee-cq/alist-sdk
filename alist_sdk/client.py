# coding: utf8
"""客户端

"""
import logging

from httpx import Client as HttpClient

logger = logging.getLogger("alist-sdk.client")


class AlistError(Exception):
    """基本错误"""


class NotLogin(AlistError):
    """未登陆"""


class RequestError(AlistError):
    """请求错误"""


class Client(HttpClient):

    def __init__(self, base_url, token=None, username=None, password=None, has_opt=False, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        if token:
            self.set_token(token)

        if username:
            if token:
                logger.warning("重复指定username, 将会忽略username和password")
            else:
                logger.info('登陆')
                self.login(username, password, has_opt)

    def verify_login_status(self) -> bool:
        """验证登陆状态, """
        me = self.get('/api/me').json()
        if me.get("code") != 200:
            logger.error("登陆失败[%d], %s", me.get("code"), me.get("message"))
            return False

        username = me['data'].get('username')
        if username not in [None]:
            logger.info("登陆成功： 当前用户： %s", username)
            return True
        logger.warning("登陆失败")
        return False

    def set_token(self, token) -> bool:
        """更新Token，Token验证成功，返回True"""
        self.headers.update({"Authorization": token})
        return self.verify_login_status()

    def me(self) -> dict:
        return self.get('/api/me').json()

    def login(self, username, password, has_opt=False) -> bool:
        """登陆，成功返回Ture"""
        endpoint = '/api/auth/login'
        res = self.post(
            url=endpoint,
            json={
                "username": username,
                "password": password,
                "opt_code": input("请输入当前OPT代码：") if has_opt else ""
            },
        )

        if res.status_code == 200 and res.json()['code'] == 200:
            return self.set_token(res.json()["data"]["token"])
        logger.warning("登陆失败[%d]：%s", res.status_code, res.text)
        return False
