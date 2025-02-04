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
    "https://www.sslproxies.org/",
    "https://www.us-proxy.org/",
    "https://free-proxy-list.net/uk-proxy.html",
    "https://free-proxy-list.net/"
]


def get_proxies_free_proxy() -> List[Proxy]:
    # Initialise wrapper and get proxies
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
            ips = soup.find('table', {'class': 'table table-striped table-bordered'})
            for row in ips.find_all("tr")[1:]:
                col = row.find_all("td")
                last_checked = {"cnt": col[7].contents[0].split(" ")[0], "unit": col[7].contents[0].split(" ")[1]}
                if (last_checked['unit'] in ['min', 'secs', 'sec']) \
                        or (int(last_checked['cnt']) <= 10 and last_checked['unit'] == 'mins'):
                    proxy = Proxy(ip=IPv4Address(col[0].contents[0]), port=int(col[1].contents[0]),
                                  country=col[2].contents[0] if len(col[2].contents) > 0 else "UNKNOWN",
                                  protocols=["https" if col[6].contents[0] == "yes" else "http"],
                                  anonymity="elite" if col[4].contents[0] == "elite proxy" else col[4].contents[0])
                    proxies.append(proxy)
            logger.info(f"After {url} totally get {len(proxies)}")
    return proxies
