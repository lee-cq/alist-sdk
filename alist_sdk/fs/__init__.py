from ..client import Client


class FS:

    def __init__(self, client: Client):
        self.client = client

    def mkdir(self, path):
        return self.client.post('/api/fs/mkdir', json={"path": path})

    def rename(self, new_name, path):
        return self.client.post('/api/fs/rename', json={
            "name": new_name,
            "path": path,
        })

    def upload_file_from_data(self, data, path, as_task=False):
        return self.client.put(
            '/api/fs/form',
            headers={"As-Task": as_task, "File-Path": path},
            files={
                "upload-file": (path, data)
            }
        )

    def list_files(self, path, password=None, page=1, per_page=0, refresh=False):
        return self.client.post('/api/fs/list', json={
            "path": path,
            "password": password,
            "page": page,
            "per_page": per_page,
            "refresh": refresh
        })

    def get_item_info(self, path, password=None):
        """"""
        return self.client.post('/api/fs/get', json={
            "path": path,
            "password": password
        })
