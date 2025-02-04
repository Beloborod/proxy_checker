import json
import math
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from ipaddress import IPv4Address
from time import time
from typing import Final, List, Union
import requests
from selenium.webdriver.common.by import By
from seleniumwire.thirdparty.mitmproxy.exceptions import TcpDisconnect, MitmproxyException, HttpReadDisconnect
from urllib3.exceptions import ReadTimeoutError
from src.wire_web_driver import DriverWrapper
from requests.exceptions import ConnectionError, SSLError, ProxyError, ReadTimeout, JSONDecodeError
import logging
from src.logger import logger_name

logger = logging.getLogger(logger_name)

PROTOCOLS: Final = ["socks4", "socks5", "http", "https"]
ANONYMITY: Final = Union["elite", "anonymous", "transparent"]


class Proxy(object):
    def __init__(self, ip: IPv4Address, port: int, country: str, protocols: List[str], anonymity: ANONYMITY):
        """
        :param ip: Ip address for proxy
        :param port: Port to connect
        :param country: Country of proxy server
        :param protocols: Available protocols
        :param anonymity: Anonymity level
        """
        for protocol in protocols:
            if protocol not in PROTOCOLS:
                raise ValueError(f"protocols must be only {PROTOCOLS}")
        self.ip = ip
        self.port = port
        self.country = country
        self.protocols = protocols
        self.anonymity = anonymity
        self._valid = None
        self._validation_time = 0

    @property
    def valid(self) -> bool:
        """
        :return: True if proxy was checked last 120 secs, else - return False
        """
        if self._valid and ((time() - self._validation_time) < 120):
            return True
        else:
            return False

    @valid.setter
    def valid(self, value: bool):
        self._valid = value
        self._validation_time = time()

    @property
    def proxy_str(self):
        """
        :return: Return proxy string to connect, like "http://127.0.0.1:1234"
        """
        return f"{self.protocols[0]}://{self.ip.__str__()}:{self.port}"

    @property
    def proxy_dict(self) -> dict:
        """
        :return: Dict with "http" and "https" keys, each store self.proxy_str
        """
        return {"http": self.proxy_str, "https": self.proxy_str}

    def save_in_mongo(self, redirected: bool = False) -> None:
        """
        Save current proxy to MongoDB
        :param redirected: True if IP after reach destination not equal proxy ip
        """
        from models.proxy import ProxyModel
        proxy_model = ProxyModel.objects.filter(ip=self.ip.__str__(), port=self.port).first()
        if proxy_model is None:
            proxy_model = ProxyModel()
        proxy_model.ip = self.ip.__str__()
        proxy_model.port = self.port
        proxy_model.protocols = self.protocols
        proxy_model.anonymity = self.anonymity
        proxy_model.country = self.country
        proxy_model.validation_date = datetime.fromtimestamp(self._validation_time)
        proxy_model.redirects = redirected
        proxy_model.save()
        logger.info(f"Save {self.proxy_str} to MONGO")

    def delete_from_mongo(self) -> None:
        """
        Delete current proxy from MongoDB
        """
        from models.proxy import ProxyModel
        proxy_model = ProxyModel.objects.filter(ip=self.ip.__str__(), port=self.port).first()
        if proxy_model is None:
            return
        proxy_model.delete()
        logger.info(f"Delete {self.proxy_str} from MONGO")


class ProxyCollection(object):
    def __init__(self, proxies: List[Proxy]=None):
        """
        Represent collection of proxies to work with it
        :param proxies:
        """
        if proxies is None:
            proxies = []
        self._proxies = proxies
        self.proxies = []
        if len(self._proxies) > 0:
            self.check_list()

    def check_list(self) -> None:
        """
        Delete duplicates from collected proxies list
        """
        for i in range(len(self._proxies)):
            cur_pr = self._proxies[i]
            for proxy in list(*self._proxies[i+1:]):
                if (proxy.ip == cur_pr.ip) and (proxy.port == cur_pr.port) and (proxy.protocols == cur_pr.protocols):
                    break
            else:
                self.proxies.append(cur_pr)

    def add_proxy(self, new_proxy: Proxy) -> None:
        """
        :param new_proxy: Proxy to add in proxies list (if not exist)
        """
        for proxy in self.proxies:
            if ((proxy.ip == new_proxy.ip) and (proxy.port == new_proxy.port)
                    and (proxy.protocols == new_proxy.protocols)):
                break
        else:
            self.proxies.append(new_proxy)

    def load_from_mongo(self) -> None:
        """
        Load currently saved proxies from MongoDB
        """
        logger.info(f"Load proxies from MONGO...")
        from models.proxy import ProxyModel
        proxy_models = ProxyModel.objects()
        for proxy_model in proxy_models:
            self.add_proxy(Proxy(IPv4Address(proxy_model.ip), proxy_model.port, proxy_model.country,
                                 proxy_model.protocols, proxy_model.anonymity))
        logger.info(f"Load proxies from MONGO")

    def validate_all(self, force: bool = False, sync_mongo: bool = False, with_web_driver: bool = False,
                     multiprocess: bool = False, max_workers: int = 10, drop_mongo: bool = False) -> None:
        """
        Validate all proxies from collected list
        :param force: If True - validate already valid proxies
        :param sync_mongo: If True - delete from mongo invalid proxies, and add valid
        :param with_web_driver: If True - use seleniumwire.webdriver instead requests
        :param multiprocess: If True - use multithreading to speedup proxy validation
        :param max_workers: Maximum of parallel threads to run, if multiprocess=True
        :param drop_mongo: If True - drop currently collected MongoDB proxies collection
        """
        if drop_mongo:
            from models.connector import connection, db_name
            connector = connection()
            connector.drop_database(db_name)
            logger.info(f"Droped DB {db_name}")

        proxies_objects: List[Proxy] = []
        proxies_list = []
        for proxy in self.proxies:
            if (not proxy.valid) or force:
                proxies_objects.append(proxy)
                proxies_list.append(proxy.proxy_dict)
        with requests.Session() as session:
            self_ip = session.get("https://httpbin.io/ip").json()['origin'].split(":")[0]

        def check_list(proxies_obj: List[Proxy], proxies_l: list = None):
            for pr in proxies_obj:
                logger.info(f"Check {pr.proxy_str}")
                try:
                    if with_web_driver:
                        with DriverWrapper(proxies_l) as driver_wrapper:
                                driver_wrapper.change_proxy(proxies_l.index(pr))
                                driver_wrapper.driver.get("https://httpbin.io/ip")
                                ip_parsed = json.loads(driver_wrapper.driver.find_element(By.TAG_NAME, "body").text)
                    else:
                        with requests.Session() as s:
                            s.proxies.update(pr.proxy_dict)
                            response = s.get("https://httpbin.io/ip", verify=False, timeout=10)
                            ip_parsed = response.json()
                    if ip_parsed['origin'].split(":")[0] == pr.ip.__str__():
                        pr.valid = True
                        if sync_mongo:
                            pr.save_in_mongo()
                        logger.info(f"VALID {pr.proxy_str}")
                    elif ip_parsed['origin'].split(":")[0] != self_ip:
                        pr.valid = True
                        if sync_mongo:
                            pr.save_in_mongo(redirected=True)
                        logger.info(f"VALID {pr.proxy_str}")
                    else:
                        pr.valid = False
                        if sync_mongo:
                            pr.delete_from_mongo()
                        logger.info(f"NOT VALID {pr.proxy_str}")
                except (SSLError, ProxyError, ConnectionError, UnboundLocalError, ConnectionResetError,
                        TcpDisconnect, MitmproxyException, HttpReadDisconnect, ReadTimeoutError, ReadTimeout,
                        JSONDecodeError):
                    pr.valid = False
                    if sync_mongo:
                        pr.delete_from_mongo()
                    logger.info(f"NOT VALID {pr.proxy_str}")
                except Exception as e:
                    pr.valid = False
                    logger.info(f"NOT VALID {pr.proxy_str}")

        try:
            if multiprocess:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    num_of_baths = math.ceil(len(proxies_objects) / max_workers)
                    logger.info(f"Start MULTITHREAD work with {max_workers} workers and {num_of_baths} baths, total count of proxies: {len(proxies_objects)}")
                    try:
                        for proxy_collection in [
                            (proxies_objects[i*max_workers:(i+1)*max_workers],
                             proxies_list[i*max_workers:(i+1)*max_workers]) for i in range(num_of_baths)]:
                            executor.submit(check_list, *proxy_collection)
                    except Exception as e:
                        logger.error(f"ERROR WHEN MULTITHREAD {traceback.format_exc()}")
            else:
                check_list(proxies_objects, proxies_list)
        except Exception as e:
            logger.error(f"ERROR WHEN UPDATE PROXIES {traceback.format_exc()}")


    def save(self, path: str = "./proxies.json") -> None:
        """
        Save currently valid proxies to file
        :param path: Path and file name to save proxies
        """
        with open(path, "w+") as f:
            generated_file = []
            for proxy in self.proxies:
                generated_file.append(
                    {
                        "ip": proxy.ip.__str__(),
                        "port": proxy.port,
                        "country": proxy.country,
                        "protocols": proxy.protocols,
                        "anonymity": proxy.anonymity
                    }
                )
            f.write(json.dumps(generated_file))

    def load(self, path: str = "./proxies.json") -> None:
        """
        Load proxies from file generated via self.save()
        :param path: Path and file name to load proxies
        """
        with open(path, "r") as f:
            proxies_list = json.loads(f.read())
            for proxy_dict in proxies_list:
                proxy = Proxy(ip=IPv4Address(proxy_dict['ip']), port=int(proxy_dict['port']),
                              country=proxy_dict['country'], protocols=proxy_dict['protocols'],
                              anonymity=proxy_dict['anonymity'])
                self.add_proxy(proxy)

    def get_proxies(self, anonymity: List[ANONYMITY] = None, protocols: list = None) -> List[Proxy]:
        """
        Filter and return currently collected proxies
        :param anonymity: Anonymity level
        :param protocols: Protocols needed
        :return: List of Proxy
        """
        if protocols:
            for protocol in protocols:
                if protocol not in PROTOCOLS:
                    raise ValueError(f"protocols must be only {PROTOCOLS}")
        filtered_proxies = []
        for proxy in self.proxies:
            if ((anonymity and (any(anonim in proxy.anonymity for anonim in anonymity))) or not anonymity) and \
                ((protocols and (any(protocol in proxy.protocols for protocol in protocols))) or not protocols):
                filtered_proxies.append(proxy)
        return filtered_proxies
