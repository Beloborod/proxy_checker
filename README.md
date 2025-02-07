# About
Opensource self-hosted proxy checker from free resources, with self-validation, store in file or MongoDB

# Content

- [Installation](#installation)
- [Configuration](#configuration)
- [Run as daemon]()
- [TODOS](#todos)

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

# Run as daemon
Checker can be run as daemon ONLY on linux (limited by multiprocessing in undetected chrome driver)

You can run in terminal: ```python daemon-main.py```

Daemon have flags. hwo can be seen by  ```python daemon-main.py -h```

Available flags and rules:

```
usage: daemon-main.py [-h] [-a] [--free-proxy | --ignore-free-proxy] [--geonode | --ignore-geonode] [--best-proxies | --ignore-best-proxies] [--thespeedx | --ignore-thespeedx] [-ml] [-ms] [-md] [-f] [-j] [-wd] [-mp]
                      [-mw MAX_WORKERS] [-sl SLEEP] [-ln LOGGER_NAME]

options:
  -h, --help            show this help message and exit
  -a, --all             Use all wrappers (exclude --ignore-<wrapper_name>)
  --free-proxy          Use Free Proxy wrapper
  --ignore-free-proxy   Do not use Free Proxy wrapper
  --geonode             Use Geonode wrapper
  --ignore-geonode      Do not use Geonode wrapper
  --best-proxies        Use Best Proxies wrapper
  --ignore-best-proxies
                        Do not use Best Proxies wrapper
  --thespeedx           Use Thespeedx wrapper
  --ignore-thespeedx    Do not use Thespeedx wrapper
  -ml, --mongo-load     Load and validate proxies from mongo, save new proxies to mongo
  -ms, --mongo-save     Save new proxies to mongo, or rewrite if currently have
  -md, --mongo-drop     Drop mongo base before validate
  -f, --force           All proxies will be validated and judged
  -j, --judge           Judge proxies
  -wd, --web-driver     Use webdriver instead request library
  -mp, --multi-process  Use multithreading to validate
  -mw, --max-workers MAX_WORKERS
                        Max workers count to multithreading
  -sl, --sleep SLEEP    Sleep time between cycles
  -ln, --logger-name LOGGER_NAME
                        Name of logger file

```

So you can run many daemons, for example via systemctl, to do some parallel tasks.

One daemon with 10 workers probably take ~1.5-2 Gb RAM

Here is example of systemctl daemon service file:
```yaml
[Unit]
Description = Get new proxies
After = network.target

[Service]
Type = simple
WorkingDirectory=<YOUR_DIRECTORY>
ExecStart = python3.12 <YOUR_DIRECTORY>/daemon-main.py -a -ms -f -mp -mw 10 -ln main_checker -sl 5
Restart = always
SyslogIdentifier = proxy_checker_main
RestartSec = 2
TimeoutStartSec = infinity
KillMode=mixed
KillSignal=SIGKILL

[Install]
WantedBy = default.target
```

On prod i'm use 2 services always: 
- for check proxies without thespeedx and current mongo (flags ```-a --ignore-thespeedx -ms -f -mp -mw 10 -ln main_checker -sl 5```)
- for revalidate current collected proxies (flags ``` -ml -ms -f -mp -mw 10 -ln mongo_checker -sl 5```)

And third, but more time it's disabled (too many proxies collected and validated every run, ~5-10k) with flags ``` --thespeedx -ms -f -mp -mw 10 -ln tsx_checker```

### TODOS
- [x] ~~Write README =)~~
- [x] ~~Add docstrings~~
- [x] ~~Add more proxy sites to parse proxy~~
- [ ] Make MongoDB not necessary
- [x] ~~Improve proxy model and validation info~~