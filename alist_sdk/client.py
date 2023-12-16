# coding: utf8
"""客户端

"""
import logging
import urllib.parse
from pathlib import Path

from httpx import Client as HttpClient
from .models import *
from .version import __version__

logger = logging.getLogger("alist-sdk.client")

__all__ = ['Client']


class Client(HttpClient):

    def __init__(self, base_url, token=None, username=None, password=None, has_opt=False, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.headers.setdefault('User-Agent', f"Alist-SDK/{__version__}")
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

    @verify()
    def verify_request(self,
                       method: str,
                       url,
                       *,
                       content=None,
                       data=None,
                       files=None,
                       json=None,
                       params=None,
                       headers=None,
                       follow_redirects=True,
                       **kwargs
                       ):
        return {}, self.request(
            method=method,
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            follow_redirects=follow_redirects,
            **kwargs
        )

    @verify()
    def me(self):
        return locals(), self.get('/api/me')

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

    # ================ FS 相关方法 =================

    @verify()
    def mkdir(self, path):
        return locals(), self.post('/api/fs/mkdir', json={"path": path})

    @verify()
    def rename(self, new_name, path):
        return locals(), self.post('/api/fs/rename', json={
            "name": new_name,
            "path": path,
        })

    @verify()
    def upload_file_form_data(self, data, path, as_task=False):
        """表单上传"""
        return locals(), self.put(
            '/api/fs/form',
            headers={"As-Task": 'true' if as_task else 'false',

                     "File-Path": urllib.parse.quote_plus(path)
                     },
            # content=data,
            files={
                "upload-file": data
            }
        )

    @verify()
    def upload_file_put(self, local_path, path, as_task=False):
        """流式上传文件"""
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(local_path)

        return locals(), self.put(
            '/api/fs/put',
            headers={"As-Task": 'true' if as_task else 'false',
                     "Content-Type": 'application/octet-stream',
                     "Last-Modified": str(int(local_path.stat(follow_symlinks=True).st_mtime * 1000)),
                     "File-Path": urllib.parse.quote_plus(path)
                     },
            content=open(local_path, 'rb'),
        )

    @verify()
    def list_files(self, path, password='', page=1, per_page=0, refresh=False):
        """POST 列出文件目录"""
        return locals(), self.post('/api/fs/list', json={
            "path": path,
            "password": password,
            "page": page,
            "per_page": per_page,
            "refresh": refresh
        })

    @verify()
    def get_item_info(self, path, password=None):
        """POST 获取某个文件/目录信息"""
        return locals(), self.post('/api/fs/get', json={
            "path": path,
            "password": password
        })

    @verify()
    def search(self, path, keyword, scope,
               page: int = None, per_page: int = None, password: str = None):
        """POST 搜索文件或文件夹

        :param password:
        :param per_page:
        :param page:
        :param keyword:
        :param path:
        :param scope: 搜索类型	0-全部 1-文件夹 2-文件
        """
        return locals(), self.post(
            "/api/fs/search",
            json={
                "parent": path,
                "keywords": keyword,
                "scope": scope,
                "page": page,
                "per_page": per_page,
                "password": password
            },
        )

    @verify()
    def get_dir(self, path, password=None, page: int = 1, per_page: int = 10, refresh: bool = False):
        """POST 获取目录 /api/fs/dirs

        :return:
        """
        return locals(), self.post(
            '/api/fs/dirs',
            json={
                "path": path,
                "password": password,
                "page": page,
                "per_page": per_page,
                "refresh": refresh
            })

    @verify()
    def batch_rename(self):
        """POST 批量重命名  POST /api/fs/batch_rename
        https://alist.nn.ci/zh/guide/api/fs.html#post-%E6%89%B9%E9%87%8F%E9%87%8D%E5%91%BD%E5%90%8D
        """
        raise NotImplemented

    @verify()
    def regex_rename(self):
        """POST 正则重命名   /api/fs/regex_rename  """
        raise NotImplemented

    @verify()
    def move(self, src_dir, dst_dir, files: list[str]):
        """POST 移动文件  /api/fs/move"""
        return locals(), self.post(
            '/api/fs/move',
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
                "names": files
            }
        )

    @verify()
    def recursive_move(self, src_dir, dst_dir):
        """POST 聚合移动"""
        return locals(), self.post(
            '/api/fs/recursive_move',
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
            }
        )

    @verify()
    def copy(self, src_dir, dst_dir, files: list[str]):
        return locals(), self.post(
            '/api/fs/copy',
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
                "names": files
            })

    @verify()
    def remove(self, path, names):
        return locals(), self.post(
            '/api/fs/remove',
            json={"names": names,
                  "dir": path
                  }
        )

    @verify()
    def remove_empty_directory(self, path):
        """/api/fs/remove_empty_directory"""
        return locals(), self.post(
            '/api/fs/remove_empty_directory',
            json={"src_dir": path}
        )

    @verify()
    def add_aria2(self, path, urls: list[str]):
        return locals(), self.post(
            '/api/fs/add_aria2',
            json={
                "urls": urls,
                "path": path
            }
        )

    @verify()
    def add_qbit(self, path, urls: list[str]):
        return locals(), self.post(
            '/api/fs/add_qbit',
            json={
                "urls": urls,
                "path": path
            }
        )

    # ================ admin/task 相关API ============================

    @staticmethod
    def task_type_verify(task_type: TaskTypeModify):
        ok = ['upload', 'copy', 'aria2_down', 'aria2_transfer', 'qbit_down', 'qbit_transfer']
        if task_type not in ok:
            raise ValueError(f"{task_type = }, not in {ok}")

    @verify()
    def task_done(self, task_type: TaskTypeModify):
        """获取已经完成的任务"""
        self.task_type_verify(task_type)
        return locals(), self.get(f'/api/admin/task/{task_type}/done')

    @verify()
    def task_undone(self, task_type: TaskTypeModify):
        """获取未完成的任务"""
        self.task_type_verify(task_type)
        return locals(), self.get(f'/api/admin/task/{task_type}/undone')

    @verify()
    def task_delete(self, task_type: TaskTypeModify, task_id):
        """删除任务"""
        self.task_type_verify(task_type)
        return locals(), self.post(f'/api/admin/task/{task_type}/delete', params={"tid": task_id})

    @verify()
    def task_cancel(self, task_type: TaskTypeModify, task_id):
        """取消任务"""
        self.task_type_verify(task_type)
        return locals(), self.post(f'/api/admin/task/{task_type}/cancel', params={"tid": task_id})

    @verify()
    def task_clear_done(self, task_type: TaskTypeModify):
        """清除已经完成的任务"""
        self.task_type_verify(task_type)
        return locals(), self.post(f'/api/admin/task/{task_type}/clear_done')

    @verify()
    def task_clear_succeeded(self, task_type: TaskTypeModify):
        """清除已成功的任务"""
        self.task_type_verify(task_type)
        return locals(), self.post(f'/api/admin/task/{task_type}/clear_succeeded')

    @verify()
    def task_retry(self, task_type: TaskTypeModify, task_id):
        """重试任务"""
        self.task_type_verify(task_type)
        return locals(), self.post(f'/api/admin/task/{task_type}/retry', params={"tid": task_id})

    # ================= admin/storages 相关 ==========================

    @verify()
    def storage_list(self):
        """列出存储器列表"""
        return locals(), self.get("/api/admin/storage/list")

    @verify()
    def storage_create(self, storage: dict | Storage):
        """创建一个存储器后端"""
        if isinstance(storage, dict):
            storage = Storage(**storage)
        return locals(), self.post(
            "/api/admin/storage/create",
            json=storage.model_dump(exclude={'id', 'modified'})
        )
