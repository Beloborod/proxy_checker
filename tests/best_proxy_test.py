import pytest
from proxy_wrappers.best_proxies import get_proxies_best_proxies


@pytest.mark.order(after=["web_driver_test.py::test_driver", "web_driver_test.py::test_driver_wrapper",
                          "proxy_object_test.py::test_proxy", "proxy_object_test.py::test_proxy_collection"])
@pytest.mark.dependency(depends=["web_driver_test.py::test_driver",
                                 "web_driver_test.py::test_driver_wrapper",
                                 "proxy_object_test.py::test_proxy",
                                 "proxy_object_test.py::test_proxy_collection"],
                        scope="session")
def test_geonode_proxy():
    assert type(get_proxies_best_proxies()) is list
