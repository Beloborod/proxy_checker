from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
from proxy_wrappers.geonode import get_proxies_geonode



if __name__ == "__main__":
    setup_logger()
    proxy_collection = ProxyCollection()

    """--- GET NEW PROXIES ---"""
    for proxy in get_proxies_free_proxy():
        proxy_collection.add_proxy(proxy)

    for proxy in get_proxies_geonode():
        proxy_collection.add_proxy(proxy)

    """--- UPDATE SAVED PROXIES ---"""
    proxy_collection.load_from_mongo()


    """--- VALIDATE ALL ---"""
    proxy_collection.validate_all(multiprocess=True, with_web_driver=False, sync_mongo=True)
