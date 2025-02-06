import sys
from time import sleep

from proxy_wrappers.thespeedx import get_proxies_thespeedx
from src.proxy import ProxyCollection
from src.logger import setup_logger
from proxy_wrappers.free_proxy import get_proxies_free_proxy
from proxy_wrappers.geonode import get_proxies_geonode
from proxy_wrappers.best_proxies import get_proxies_best_proxies
import argparse


args_parser = argparse.ArgumentParser()
args_parser.add_argument('-a', '--all', action='store_true',
                         help='Use all wrappers (exclude --ignore-<wrapper_name>)')

free_proxy = args_parser.add_mutually_exclusive_group()
free_proxy.add_argument('--free-proxy', action='store_true', help='Use Free Proxy wrapper')
free_proxy.add_argument('--ignore-free-proxy', action='store_true', help='Do not use Free Proxy wrapper')

geonode = args_parser.add_mutually_exclusive_group()
geonode.add_argument('--geonode', action='store_true', help='Use Geonode wrapper')
geonode.add_argument('--ignore-geonode', action='store_true', help='Do not use Geonode wrapper')

best_proxy = args_parser.add_mutually_exclusive_group()
best_proxy.add_argument('--best-proxies', action='store_true', help='Use Best Proxies wrapper')
best_proxy.add_argument('--ignore-best-proxies', action='store_true',
                        help='Do not use Best Proxies wrapper')

thespeedx = args_parser.add_mutually_exclusive_group()
thespeedx.add_argument('--thespeedx', action='store_true', help='Use Thespeedx wrapper')
thespeedx.add_argument('--ignore-thespeedx', action='store_true', help='Do not use Thespeedx wrapper')

args_parser.add_argument('-ml', '--mongo-load', action='store_true',
                         help='Load and validate proxies from mongo, save new proxies to mongo')

args_parser.add_argument('-ms', '--mongo-save', action='store_true',
                         help='Save new proxies to mongo, or rewrite if currently have')

args_parser.add_argument('-md', '--mongo-drop', action='store_true',
                         help='Drop mongo base before validate')

args_parser.add_argument('-f', '--force', action='store_true',
                         help='All proxies will be validated and judged')

args_parser.add_argument('-j', '--judge', action='store_true',
                         help='Judge proxies')

args_parser.add_argument('-wd', '--web-driver', action='store_true',
                         help='Use webdriver instead request library')

args_parser.add_argument('-mp', '--multi-process', action='store_true',
                         help='Use multithreading to validate',
                         required=('--max-workers' in sys.argv) or ('-mw' in sys.argv))

args_parser.add_argument('-mw', '--max-workers',  help='Max workers count to multithreading', type=int)

args_parser.add_argument('-sl', '--sleep',  help='Sleep time between cycles', type=float, default=0.1)

args_parser.add_argument('-ln', '--logger-name',  help='Name of logger file', default='proxy_checker')




args = args_parser.parse_args()


setup_logger(logger_file=args.logger_name)
last_commit = "nothing"


while True:
    try:
        proxy_collection = ProxyCollection()

        if (args.all or args.free_proxy) and (not args.ignore_free_proxy):
            for proxy in get_proxies_free_proxy():
                proxy_collection.add_proxy(proxy)

        if (args.all or args.geonode) and (not args.ignore_geonode):
            for proxy in get_proxies_geonode():
                proxy_collection.add_proxy(proxy)

        if (args.all or args.best_proxies) and (not args.ignore_best_proxies):
            for proxy in get_proxies_best_proxies():
                proxy_collection.add_proxy(proxy)

        if (args.all or args.thespeedx) and (not args.ignore_thespeedx):
            thespeedx_proxies, last_commit = get_proxies_thespeedx(last_commit)
            for proxy in thespeedx_proxies:
                proxy_collection.add_proxy(proxy)

        if args.mongo_load:
            proxy_collection.load_from_mongo()


        proxy_collection.validate_all(args.force, args.mongo_save, args.web_driver, args.multi_process,
                                      args.max_workers, args.mongo_drop, args.judge)

        sleep(args.sleep)
    except KeyboardInterrupt:
        sys.exit(0)
