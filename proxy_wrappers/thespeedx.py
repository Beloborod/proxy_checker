import json
from ipaddress import IPv4Address
from typing import List, Final, Union, Tuple
from src.wire_web_driver import DriverWrapper
from bs4 import BeautifulSoup
from src.proxy import Proxy
import logging
from src.logger import logger_name
from selenium.webdriver.common.by import By

logger = logging.getLogger(logger_name)


# Define URLS to parse and wrap proxies lists
URLS_TO_WRAP: Final = {
    "http": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "socks4": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "socks5": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
}


def get_proxies_thespeedx(last_parsed_commit: str = None) -> Union[List[Proxy], Tuple[List[Proxy], str]]:
    proxies = []
    with DriverWrapper() as driver_wrapper:
        if last_parsed_commit:
            driver_wrapper.driver.get("https://api.github.com/repos/TheSpeedX/SOCKS-List/commits")
            new_commit = json.loads(driver_wrapper.driver.find_element(By.TAG_NAME, "body").text)
            new_commit = new_commit[0]['sha']
            if new_commit == last_parsed_commit:
                return proxies, new_commit
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
    if last_parsed_commit:
        return proxies, new_commit
    else:
        return proxies

