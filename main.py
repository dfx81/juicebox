from io import TextIOWrapper
import multiprocessing
import os
import sys

from core.api_server import ApiServer
from core.config import Config
from core.discovery_server import DiscoveryServer

def main():
    config: Config = Config()

    null_file: TextIOWrapper = open(os.devnull, "w")
    sys.stderr = null_file

    discoveryProcess: multiprocessing.Process = multiprocessing.Process(target=start_discovery, args=(config,))
    apiProcess: multiprocessing.Process = multiprocessing.Process(target=start_api, args=(config,))

    discoveryProcess.start()
    apiProcess.start()

    try:
        discoveryProcess.join()
        apiProcess.join()
    except KeyboardInterrupt:
        print("[i] Shutting down Juicebox")
        discoveryProcess.terminate()
        apiProcess.terminate()
        print("[i] Juicebox has been terminated")

def start_discovery(config: Config):
    discoveryServer: DiscoveryServer = DiscoveryServer(config)
    discoveryServer.start()

def start_api(config: Config):
    apiServer: ApiServer = ApiServer(config)
    apiServer.start()

if __name__ == "__main__":
    main()