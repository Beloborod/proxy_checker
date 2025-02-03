from ipaddress import IPv4Address
from src.proxy import Proxy, ProxyCollection
import pytest


@pytest.mark.dependency(scope='session')
def test_proxy():
    assert type(Proxy(IPv4Address("127.0.0.1"), 80, "RU", ["https"], "elite")) is Proxy


@pytest.mark.dependency(scope='session')
def test_proxy_collection():
    assert type(ProxyCollection()) is ProxyCollection