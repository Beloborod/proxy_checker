import pytest
from proxy_wrappers.thespeedx import get_proxies_thespeedx


@pytest.mark.order(after=["web_driver_test.py::test_driver", "web_driver_test.py::test_driver_wrapper",
                          "proxy_object_test.py::test_proxy", "proxy_object_test.py::test_proxy_collection"])
@pytest.mark.dependency(depends=["web_driver_test.py::test_driver",
                                 "web_driver_test.py::test_driver_wrapper",
                                 "proxy_object_test.py::test_proxy",
                                 "proxy_object_test.py::test_proxy_collection"],
                        scope="session")
def test_thespeedx_proxy():
    assert type(get_proxies_thespeedx()) is list


@pytest.mark.order(after=["web_driver_test.py::test_driver", "web_driver_test.py::test_driver_wrapper",
                          "proxy_object_test.py::test_proxy", "proxy_object_test.py::test_proxy_collection"])
@pytest.mark.dependency(depends=["web_driver_test.py::test_driver",
                                 "web_driver_test.py::test_driver_wrapper",
                                 "proxy_object_test.py::test_proxy",
                                 "proxy_object_test.py::test_proxy_collection"],
                        scope="session")
def test_thespeedx_proxy_last_commit():
    assert type(get_proxies_thespeedx("test")) is tuple
