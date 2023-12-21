from alist_sdk import Client
from alist_sdk.tools.models import Configs


class ExtraClient(Client):

    def export_configs(self) -> Configs:
        pass

    def import_configs(self, configs: Configs):
        pass
