import pytest
import logging

from .client import Client

logging.basicConfig(level="INFO")

client = Client("http://localhost:5244", username='admin', password="123456", verify=False)


def test_login():
    _client = Client("http://localhost:5244", verify=False)
    assert _client.login(username='admin', password="123456", ), "登陆失败"


def test_me():
    client.me()
