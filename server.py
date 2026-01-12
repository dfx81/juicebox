from io import TextIOWrapper
import multiprocessing
import os
import subprocess
import sys
import vlc

from core.api_server import ApiServer
from core.config import Config
from core.discovery_server import DiscoveryServer

def main():
    config: Config = Config()

    null_file: TextIOWrapper = open(os.devnull, "w")
    # sys.stderr = null_file

    try:
        if not check_ffmpeg(config, out=null_file):
            raise NameError("ffmpeg Not Installed.")
        
        vlc.libvlc_get_version()

        multiprocessing.freeze_support()

        discovery_process: multiprocessing.Process = multiprocessing.Process(target=start_discovery, args=(config, ))
        api_process: multiprocessing.Process = multiprocessing.Process(target=start_api, args=(config, ))

        discovery_process.start()
        api_process.start()
    
        try:
            discovery_process.join()
            api_process.join()
        except KeyboardInterrupt:
            print("[i] Shutting down Juicebox")
        finally:
            discovery_process.terminate()
            api_process.terminate()
            print("[i] Juicebox has been terminated")
    except NameError as err:
        print(f"[!] Make sure VLC and ffmpeg are installed")
        exit(-1)

def start_discovery(config: Config):
    discovery_server: DiscoveryServer = DiscoveryServer(config)
    discovery_server.start()

def start_api(config: Config):
    api_server: ApiServer = ApiServer(config)
    api_server.start()

def check_ffmpeg(config: Config, out: TextIOWrapper) -> bool:
    try:
        return subprocess.call([os.path.join(config.server.ffmpeg, f"ffmpeg{".exe" if os.name == "nt" else ""}") if config.server.ffmpeg else "ffmpeg", "-version"], stdout=out) == 0
    except Exception:
        return False

if __name__ == "__main__":
    try:
        main()
    except ValueError as err:
        print(err)
