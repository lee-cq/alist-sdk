import urllib.parse
from pathlib import Path

from .model import *


class FS(BaseFS):
    @verify()
    def mkdir(self, path):
        return locals(), self.client.post('/api/fs/mkdir', json={"path": path})

    @verify()
    def rename(self, new_name, path):
        return locals(), self.client.post('/api/fs/rename', json={
            "name": new_name,
            "path": path,
        })

    @verify()
    def upload_file_form_data(self, data, path, as_task=False):
        """表单上传"""
        return locals(), self.client.put(
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

        return locals(), self.client.put(
            '/api/fs/put',
            headers={"As-Task": 'true' if as_task else 'false',
                     "Content-Type": 'application/octet-stream',
                     "Last-Modified": str(int(local_path.stat(follow_symlinks=True).st_mtime * 1000)),
                     "File-Path": urllib.parse.quote_plus(path)
                     },
            content=open(local_path, 'rb'),
        )

    @verify()
    def list_files(self, path, password=None, page=1, per_page=0, refresh=False):
        """POST 列出文件目录"""
        return locals(), self.client.post('/api/fs/list', json={
            "path": path,
            "password": password,
            "page": page,
            "per_page": per_page,
            "refresh": refresh
        })

    @verify()
    def get_item_info(self, path, password=None):
        """POST 获取某个文件/目录信息"""
        return locals(), self.client.post('/api/fs/get', json={
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
        return locals(), self.client.post(
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
        return locals(), self.client.post(
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
        return locals(), self.client.post(
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
        return locals(), self.client.post(
            '/api/fs/recursive_move',
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
            }
        )

    @verify()
    def copy(self, src_dir, dst_dir, files: list[str]):
        return locals(), self.client.post(
            '/api/fs/copy',
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
                "names": files
            })

    @verify()
    def remove(self, path, names):
        return locals(), self.client.post(
            '/api/fs/remove',
            json={"names": names,
                  "dir": path
                  }
        )

    @verify()
    def remove_empty_directory(self, path):
        """/api/fs/remove_empty_directory"""
        return locals(), self.client.post(
            '/api/fs/remove_empty_directory',
            json={"src_dir": path}
        )

    @verify()
    def add_aria2(self, path, urls: list[str]):
        return locals(), self.client.post(
            '/api/fs/add_aria2',
            json={
                "urls": urls,
                "path": path
            }
        )

    @verify()
    def add_qbit(self, path, urls: list[str]):
        return locals(), self.client.post(
            '/api/fs/add_qbit',
            json={
                "urls": urls,
                "path": path
            }
        )
