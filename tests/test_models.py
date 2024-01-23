from datetime import datetime
from pathlib import PurePosixPath, Path
import json

import pytest

from alist_sdk.models import *
from alist_sdk import models

MODEL_SIMPLE = Path(__file__).parent.joinpath("models_simple")


class TestModel:
    @pytest.mark.parametrize(
        "item",
        json.loads(MODEL_SIMPLE.joinpath("Items.json").read_text()),
        ids=lambda item: item.get("name"),
    )
    def test_item(self, item):
        a = Item(**item)
        assert isinstance(a.full_name, PurePosixPath)
        assert a.full_name.as_posix()
        assert isinstance(a.model_dump_json(), str)
        assert isinstance(a.created, datetime)
        print(a)

    @pytest.mark.parametrize(
        "list_item",
        json.loads(MODEL_SIMPLE.joinpath("ListItems.json").read_text()),
        ids=lambda item: item.get("provider"),
    )
    def test_list_item(self, list_item):
        list_items = ListItem(**list_item)
        assert isinstance(list_items, ListItem)
        list_items.model_dump_json()

    @pytest.mark.parametrize(
        "raw_item",
        json.loads(MODEL_SIMPLE.joinpath("RawItems.json").read_text()),
        ids=lambda s: s.get("name"),
    )
    def test_raw_item(self, raw_item):
        """"""
        item = RawItem(**raw_item)
        assert item.name == raw_item.get("name")
        item.model_dump_json()

    @pytest.mark.parametrize(
        "hash_info", json.loads(MODEL_SIMPLE.joinpath("HashInfos.json").read_text())
    )
    def test_hash_info(self, hash_info):
        h = HashInfo(**hash_info)
        h.model_dump_json()

    @pytest.mark.parametrize(
        "me", json.loads(MODEL_SIMPLE.joinpath("Me.json").read_text())
    )
    def test_me(self, me):
        Me(**me)

    @pytest.mark.parametrize(
        "storage", json.loads(MODEL_SIMPLE.joinpath("Storages.json").read_text())
    )
    def test_storage(self, storage):
        """"""
        _s = Storage(**storage)
        _s.model_dump_json()

    @pytest.mark.parametrize(
        "url, model, resp",
        json.loads(MODEL_SIMPLE.joinpath("Resps.json").read_text()),
        ids=lambda x: x if isinstance(x, str) else "",
    )
    def test_resp(self, url, model, resp):
        _resp = Resp(**resp)
        if _resp.code == 200:
            assert isinstance(
                _resp.data[0] if isinstance(_resp.data, list) else _resp.data,
                getattr(models, model),
            ), "Model 验证失败~"
