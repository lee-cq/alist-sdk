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
    3. UPDATE: 更新AlistPath.__repl__方法.
    4. UPDATE: 更新AlistPath.添加新的方法 set_stat，可以自定义设置stat属性，加快速度。
    5. UPDATE: 更新AlistPath.iterdir，在迭代时添加stat数据，加快速度。
    6. UPDATE: 更新AlistPath.stat，不再使用/api/fs/get 接口
    7. UPDATE: 限制alist_sdk.Client 和 alist_sdk.AsyncClient在多线程和协程中的并发量，默认30.


0.32.12:
    1. 添加Client.dict_files_items方法，以获取目录下的文件列表。
    2. 解决AListPath使用URL编码问题，现在可以正常使用中文路径。
    3. 修复AlistPath.stat() & AlistPath.raw_stat() 的缓存问题。
    4. 修复tools.config.import_configs_from_dict无法忽略本地存储的错误。
    5. Client Put AsTask 修复
    6. Verify 日志优化

0.36.13:
    1. alist版本支持到3.36.0
    2. 现在可以使用AlistPath(path, username="", password="", token="")的方式快速登录。
    3. 登录失败现在抛出异常。
    4. #3 Bugfix 为models中的全部可选字段添加默认值。

0.36.14:
    1. Client API 现在增加属性获取服务端版本: client.server_version
    2. 异步客户端添加 client.login_username 属性。
    3. 移除为保持兼容的 alist_sdk.path_lib_old.py 文件
    4. 添加测试
    5. TaskStateModify添加新的状态8
    6. AlistPath.re_stat()移除list_file调用。

0.36.15:
    1. 实现CLI命令行工具 alist-cli，可以快速登录、列出文件
    2. 细节日志优化
    3. 全局超时时间增加到30秒
    4. 修复AlistPath.__repl__ 在相对目录时报错的问题。
    5. 在pyproject.toml中为alist-cli提供命令行入口。
    6. 实现更多命令行工具，上传、下载、删除、创建目录, 打印文本文件。
    7. 在README中添加CLI命令行工具的使用说明。
    8. 对保存在本地的配置文件进行加密存储。
    9. 添加CLI命令 - version, server-version
    10. 解决新版本的alist中 Client.service_version 返回Beta版本的问题。
    11. init_alist.sh 现在默认安装3.27.2版本。
"""

__version__ = "0.37.15"

ALIST_VERSION = "v3.37.2"
