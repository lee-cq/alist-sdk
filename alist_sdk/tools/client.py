from alist_sdk import Client
from alist_sdk.tools.models import Configs
from alist_sdk.tools.configs import export_configs, import_configs_from_dict


class ExtraClient(Client):
    def export_configs(self) -> Configs:
        return export_configs(self)

    def export_config_json(self) -> str:
        return self.export_configs().model_dump_json(indent=2)

    def import_configs(self, configs):
        return import_configs_from_dict(self, configs)

    def import_config_from_other_client(
        self,
        base_url,
        token=None,
        username=None,
        password=None,
        has_opt=False,
        **kwargs,
    ):
        other_client = self.__class__(
            base_url, token, username, password, has_opt, **kwargs
        )
        return self.import_configs(
            other_client.export_configs().model_dump(mode="json")
        )
