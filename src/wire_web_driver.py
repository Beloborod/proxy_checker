from typing import TypedDict, List
from seleniumwire import webdriver
from typing import Union


PROXY_LIST = List[TypedDict("PROXY_LIST", {'http': str, 'https': str})]


class Driver(webdriver.Chrome):
    def __init__(self, proxy: PROXY_LIST = None):
        """
        Represent Chrome driver to access sites
        :param proxy: Proxy to connect
        """
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        options = webdriver.ChromeOptions()
        
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f'--user-agent={agent}')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument("--ignore-certificate-errors")

        if proxy:
            webdriver.Chrome.__init__(self, options=options, seleniumwire_options={
                'proxy': proxy[0],
            })
        else:
            webdriver.Chrome.__init__(self, options=options, seleniumwire_options={})


class DriverWrapper(object):
    def __init__(self, proxy: PROXY_LIST = None):
        """
        Wrapper for driver
        :param proxy: List of Proxies to rotate 'on-fly'
        """
        self.proxies = proxy
        self.driver: Union[Driver, None] = None

    def __enter__(self) -> object:
        self.driver = self._get_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.driver.close()
        del self.driver
        return True

    def _get_driver(self) -> Driver:
        """
        :return: new Driver object
        """
        driver = Driver(self.proxies)
        driver.set_page_load_timeout(10)
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

    def new_proxy_list(self, proxy: PROXY_LIST) -> object:
        """
        Recreate driver with new proxy list
        :param proxy: List of proxies
        :return: self
        """
        self.driver.close()
        del self.driver
        self.proxies = proxy
        self.driver = self._get_driver()
        return self
