# About
Opensource self-hosted proxy checker from free resources, with self-validation, store in file or MongoDB

# Installation
1) Clone repo via ssh ```git@github.com:Beloborod/proxy_checker.git```\
or via https ```https://github.com/Beloborod/proxy_checker.git```

2) Install MongoDB on your PC

3) Edit [connector.py](models/connector.py) file to add your MongoDB configuration

4) Install requirements ```pip install -r requirements.txt```

5) Run it via ```python main.py``` to once update your MongoDB collection with proxies, or made your own executor (look [configuration topic](#configuration) to know how configure it)


# Configuration
If you want to create your own executable file, you need in it:

- Import requirements
```python
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
... # (another proxy wrappers imports)
```
- Setup logger to collect logs in work
```python
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
... # (another proxy wrappers imports)

setup_logger()
```
- Create exemplar of ProxyCollection class, to work with proxies
```python
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
... # (another proxy wrappers imports)

setup_logger()
proxy_collection = ProxyCollection()
```
- Now, you need to collect new proxies from the internet resources. All collectors stored in [proxy_wrappers](proxy_wrappers) folder and return list of proxies. For example, here only proxies from [free_proxy](proxy_wrappers/free_proxy.py) module imported
```python
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
... # (another proxy wrappers imports)

setup_logger()
proxy_collection = ProxyCollection()

for proxy in get_proxies_free_proxy():
    proxy_collection.add_proxy(proxy)
```
- You can load from MongoDB currently stored proxies
```python
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
... # (another proxy wrappers imports)

setup_logger()
proxy_collection = ProxyCollection()

for proxy in get_proxies_free_proxy():
    proxy_collection.add_proxy(proxy)
    
proxy_collection.load_from_mongo()
```
- And finally you can validate proxies
```python
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
... # (another proxy wrappers imports)

setup_logger()
proxy_collection = ProxyCollection()

for proxy in get_proxies_free_proxy():
    proxy_collection.add_proxy(proxy)
    
proxy_collection.load_from_mongo()

proxy_collection.validate_all(
    force=False,  # Validate proxy even if it's currently valid
    sync_mongo=False,  # Add valid proxy to MongoDB, and remove invalid from MongoDB
    with_web_driver=False,  # Use seleniumwire.webdriver instead requests to validate proxies
    multiprocess=False,  # Use multithreading library to speedup validating, STRONGLY RECOMMENDED
    max_workers=10,  # Maximum of parallel threads to run, if multiprocess=True
    drop_mongo=False  # Drop current MongoDB proxy collection before validating
)
```
- You can save valid proxies to file, and load from it late
```python
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
... # (another proxy wrappers imports)

setup_logger()
proxy_collection = ProxyCollection()

for proxy in get_proxies_free_proxy():
    proxy_collection.add_proxy(proxy)
    
proxy_collection.load_from_mongo()

proxy_collection.validate_all()

proxy_collection.save("proxies.json")
proxy_collection.load("proxies.json")
```
### TODOS
- [x] ~~Write README =)~~
- [x] ~~Add docstrings~~
- [ ] Add more proxy sites to parse proxy
- [ ] Make MongoDB not necessary