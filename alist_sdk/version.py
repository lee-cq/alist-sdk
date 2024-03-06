"""

0.30.4:
    path_lib.AlistPath.write_* 支持as_task参数

0.30.5:
    path_lib.AlistPath.read_* 自动跟随重定向，确保读取真实文件内容
    path_lib.AlistPath.as_download_uri() 返回添加签名

0.30.6:
    path_lib.py 重构，以支持3.12
    将AlistPath* 添加到 __init__.py 中。

0.30.7:
    AlistPath 实现了 mkdir, touch, unlink 方法, 并测试
    BUGFIX: client remove 方法参数错误
    path_lib 添加AlistPathType 以适配 Pydantic 。
    验证器现在将 /api/admin/task/ 返回None的data转换为[]

0.30.8 & 0.30.9:
    AlistPath: 实现relative_to -> str
    AlistPath: 实现rename
    pydantic类型支持： AbsAlistPathType, AlistPathType
    AlistPath: 实现re_stat() 以强制刷新缓存
    测试的alist端口更新为5245，防止多个服务冲突。
    AlistPath 添加构造器 - from_client

0.30.10:
    1. 现在AlistPath.write_bytes() 支持接收Path对象，读取文件并写入远程
    2. UPDATE:path_lib.login_server() 防止重复登陆
    3. BUGFIX: AlistPath.exists() 现在引用 re_stat()，以检查最新的状态
    4. AlistPath 允许递归创建目录
    5. AlistPath.as_download_uri -> get_download_uri, 获取方式更新。
    6. BUGFIX: 获取下载URL错误
    7. 客户端添加方法：admin_storage_update, admin_storage_delete
    8. 现在AlistPath.stat(force=False, retry=1, timeout=0.1): 在默认情况下获取不到文件,对象将会在0.1秒后重试一次.
    9. 现在AlistPath.re_stat(retry=1, timeout=1) == stat(True, 1, 1)
    10. 现在 tools.config.import_config 将忽略本地存储和任何key=id
    11. 当新文件出现在新的存储器中的时候,需要强制刷新list


0.30.11:
    1. BUGFIX: 从其他站点导入配置时，数据模型错误。
    2. BUGFIX: http://localhost:5244 无法正常识别
    3. UPDATE: 更新AplistPath.__repl__方法.
    4. UPDATE: 更新AlistPath.添加新的方法 set_stat，可以自定义设置stat属性，加快速度。
    5. UPDATE: 更新AlistPath.iterdir，在迭代时添加stat数据，加快速度。
    6. UPDATE: 更新AlistPath.stat，不再使用/api/fs/get 接口
    7. UPDATE: 限制alist_sdk.Client 和 alist_sdk.AsyncClient在多线程和协程中的并发量，默认30.

"""

__version__ = "0.30.11"

ALIST_VERSION = "v3.32.0"
