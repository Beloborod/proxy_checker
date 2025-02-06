import logging
from typing import TypedDict, List, Self
from seleniumwire import undetected_chromedriver
from typing import Union
from selenium_stealth import stealth
from platform import system
from src.logger import logger_name
import os
import signal

logger = logging.getLogger(logger_name)

PROXY_LIST = List[TypedDict("PROXY_LIST", {'http': str, 'https': str})]


class Driver(undetected_chromedriver.Chrome):
    def __init__(self, proxy: PROXY_LIST = None):
        """
        Represent Chrome driver to access sites
        :param proxy: Proxy to connect
        """
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        options = undetected_chromedriver.ChromeOptions()
        
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f'--user-agent={agent}')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--enable-javascript")

        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-crash-reporter")
        options.add_argument("--disable-oopr-debug-crash-dump")
        options.add_argument("--no-crash-upload")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-low-res-tiling")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")

        if proxy:
            super().__init__(use_subprocess=True, options=options, seleniumwire_options={
                'proxy': proxy[0],
            }, version_main=132)
        else:
            super().__init__(use_subprocess=True, options=options, version_main=132)


class DriverWrapper(object):
    def __init__(self, proxy: PROXY_LIST = None):
        """
        Wrapper for driver
        :param proxy: List of Proxies to rotate 'on-fly'
        """
        self.proxies = proxy
        self.driver: Union[Driver, None] = None

    def __enter__(self) -> Self:
        self.driver = self._get_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close_driver()
        return True

    def close_driver(self):
        pid = self.driver.browser_pid
        if system() == 'Linux':
            os.kill(pid, signal.SIGKILL)
            print("kill", pid)
        elif system() == 'Windows':
            os.kill(pid, signal.SIGKILL)
        else:
            logger.fatal(f'SYSTEM {system()} UNKNOWN, MEMORY LEAK PROBLEM')
        self.driver.quit()
        del self.driver
        print("deleted quited")

    def _get_driver(self) -> Driver:
        """
        :return: new Driver object
        """
        driver = Driver(self.proxies)
        driver.set_page_load_timeout(10)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return driver

    def change_proxy(self, proxy_index: int) -> bool:
        """
        Change proxy to any from list, given when init or after coll self.new_proxy_list
        :param proxy_index: Index from self.proxies list
        :return: True, if proxy successfully changed
        """
        if len(self.proxies) > proxy_index:
            self.driver.proxy = self.proxies[proxy_index]
        else:
            raise IndexError(f"Current list of proxies contains {len(self.proxies)} elements, but called {proxy_index}")
        return True

    def new_proxy_list(self, proxy: PROXY_LIST) -> Self:
        """
        Recreate driver with new proxy list
        :param proxy: List of proxies
        :return: self
        """
        self.close_driver()
        self.proxies = proxy
        self.driver = self._get_driver()
        return self
