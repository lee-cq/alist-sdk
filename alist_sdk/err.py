class AlistError(Exception):
    """基本错误"""


class NotLogin(AlistError):
    """未登陆"""


class RequestError(AlistError):
    """请求错误"""
