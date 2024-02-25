"""

0.30.4:
    path_lib.AlistPath.write_* 支持as_task参数

0.30.5:
    path_lib.AlistPath.read_* 自动跟随重定向，确保读取真实文件内容
    path_lib.AlistPath.as_download_uri() 返回添加签名

0.30.6:
    path_lib.py 重构，以支持3.12
    将AlistPath* 添加到 __init__.py 中。
"""

__version__ = "0.30.6"

ALIST_VERSION = "v3.30.0"
