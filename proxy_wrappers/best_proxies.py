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
URLS_TO_WRAP: Final = [
    "https://best-proxies.ru/proxylist/free/"
]


def get_proxies_best_proxies() -> List[Proxy]:
    with DriverWrapper() as driver_wrapper:
        proxies = []
        for url in URLS_TO_WRAP:
            logger.info(f"Connect to {url}")
            try:
                driver_wrapper.driver.get(url)
                WebDriverWait(driver_wrapper.driver, 10).until(
                    expected_conditions.presence_of_element_located((By.ID, 'page-content')))
            except Exception as e:
                logger.fatal(f"{url} is unavailable")
                continue
            soup = BeautifulSoup(driver_wrapper.driver.page_source, 'html.parser')
            protocols = soup.find_all('div', {'class': 'col-xs-12 col-sm-6 col-md-3'})
            for protocol in iter(protocols):
                for ip in protocol.find('textarea', {'class': 'form-control'}).text.split("\n"):
                    proxy = Proxy(ip=IPv4Address(ip.split(":")[0]), port=int(ip.split(":")[1]),
                                  country="UNKNOWN",
                                  protocols=[protocol.find('h3', {'class': 'text-left'}).text.lower()],
                                  anonymity="UNKNOWN")
                    proxies.append(proxy)
            logger.info(f"After {url} totally get {len(proxies)}")
    return proxies
