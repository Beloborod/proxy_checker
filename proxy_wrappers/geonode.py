import json
import time
import traceback
from ipaddress import IPv4Address
from typing import List, Final
from src.wire_web_driver import DriverWrapper
from bs4 import BeautifulSoup
from src.proxy import Proxy
import logging
from src.logger import logger_name

logger = logging.getLogger(logger_name)


# Define URLS to parse and wrap proxies lists
URLS_TO_WRAP: Final = [
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
]


def get_proxies_geonode() -> List[Proxy]:
    with DriverWrapper() as driver_wrapper:
        proxies = []
        for url in URLS_TO_WRAP:
            logger.info(f"Connect to {url}")
            try:
                driver_wrapper.driver.get(url)
            except Exception as e:
                logger.fatal(f"{url} is unavailable")
                continue
            soup = BeautifulSoup(driver_wrapper.driver.page_source, 'html.parser')
            data = json.loads(soup.text)['data']
            for proxy_dict in data:
                if (time.time() - proxy_dict["lastChecked"]) <= 2*60:
                    proxy = Proxy(ip=IPv4Address(proxy_dict['ip']), port=int(proxy_dict['port']),
                                  country=proxy_dict['country'] if 'country' in proxy_dict.keys() else "UNKNOWN",
                                  protocols=proxy_dict['protocols'],
                                  anonymity=proxy_dict['anonymityLevel'])
                    proxies.append(proxy)
        return proxies
