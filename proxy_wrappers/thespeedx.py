import traceback
from ipaddress import IPv4Address
from typing import List, Final
from src.wire_web_driver import DriverWrapper
from bs4 import BeautifulSoup
from src.proxy import Proxy
import logging
from src.logger import logger_name
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

logger = logging.getLogger(logger_name)


# Define URLS to parse and wrap proxies lists
URLS_TO_WRAP: Final = {
    "http": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "socks4": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "socks5": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
}


def get_proxies_thespeedx() -> List[Proxy]:
    with DriverWrapper() as driver_wrapper:
        proxies = []
        for protocol, url in URLS_TO_WRAP.items():
            logger.info(f"Connect to {url}")
            try:
                driver_wrapper.driver.get(url)
            except Exception as e:
                logger.fatal(f"{url} is unavailable")
                continue
            soup = BeautifulSoup(driver_wrapper.driver.page_source, 'html.parser')
            for ip in soup.text.split("\n"):
                if ip != "":
                    proxy = Proxy(ip=IPv4Address(ip.split(":")[0]), port=int(ip.split(":")[1]),
                                  country="UNKNOWN",
                                  protocols=[protocol],
                                  anonymity="UNKNOWN")
                    proxies.append(proxy)
            logger.info(f"After {url} totally get {len(proxies)}")
    return proxies

