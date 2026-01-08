import getpass
from io import TextIOWrapper
import multiprocessing
import os
import sys

from core.api_server import ApiServer
from core.client import Client
from core.config import Config
from core.discovery_server import DiscoveryServer
from core.utils import get_app_version

def serve(config):
    null_file: TextIOWrapper = open(os.devnull, "w")
    sys.stderr = null_file

    api_server: ApiServer
    discovery_server: DiscoveryServer

    try:
        api_server = ApiServer(config)
    except NameError as err:
        print(f"[!] {err}")
        exit(-1)

    try:
        discovery_server = DiscoveryServer(config)
    except Exception as err:
        print(f"[!] {err}")
        exit(-1)

    discovery_process: multiprocessing.Process = multiprocessing.Process(target=discovery_server.start)
    api_process: multiprocessing.Process = multiprocessing.Process(target=api_server.start)

    try:
        discovery_process.start()
        api_process.start()
        discovery_process.join()
        api_process.join()
    except KeyboardInterrupt:
        print("[i] Shutting down Juicebox")
    finally:
        discovery_process.terminate()
        api_process.terminate()
        print("[i] Juicebox has been terminated")

if __name__ == "__main__":
    config: Config = Config()
    serve(config)