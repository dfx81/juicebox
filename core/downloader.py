import os
import json
import socket
import threading
import yt_dlp

from yt_dlp.utils import DownloadError, ExtractorError
from core.config import Config
from core.player import Player

class Downloader:
    def __init__(self, config: Config, player: Player):
        self._config: Config = config
        self._player: Player = player
        self._setup()
    
    def _setup(self):
        self._lock: threading.Lock = threading.Lock()
        self._path: str = self._config.storage.downloads
        os.makedirs(self._path, exist_ok=True)
        self._urls: list[str] = []
        self._requestors: list[dict] = []
        self._busy: bool = False

    def queue(self, url: str, requestor: str):
        self._urls.append(url)

        id: str = self._get_id_from_url(url)

        self._requestors.append({
            "requestor": requestor,
            "id": id
        })

        if not self._busy:
            while self._urls:
                self._download()

    def _download_progress(self, info: dict):
        if info["status"] == "finished":
            print(f"[i] Finished Downloading {info["info_dict"]["id"]}")
            with open(f"{self._path}{os.sep}{info["info_dict"]["id"]}.json", "w", encoding="utf-8") as file:
                json.dump({
                    "id": info["info_dict"]["id"],
                    "title": info["info_dict"]["title"],
                    "duration": info["info_dict"]["duration_string"],
                    "channel": info["info_dict"]["channel"],
                    "url": info["info_dict"]["original_url"]
                }, file, ensure_ascii=False, indent=4)

    def _post_hook(self, file_name: str):
        print(f"[i] Queued {file_name}")

        id: str = file_name.split(os.sep)[-1].split(".")[0]

        info: dict[str, str] = {}

        self._lock.acquire()
        for requestor_info in self._requestors:
            if requestor_info["id"] == id:
                info = requestor_info
                break

        if info:
            self._requestors.remove(info)
        
        self._lock.release()
        self._player.queue(file_name, info["requestor"])

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1)

            message: str = f"UPDATE|Queue updated"
            sock.sendto(str.encode(message), ("255.255.255.255", self._config.client.port))

    def _check_exist(self, file: str):
        return os.path.isfile(file)
    
    def get_urls_in_playlist(self, url: str) -> list[str]:
        urls: list[str] = []

        with yt_dlp.YoutubeDL({
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "break_per_url": True,
            "logtostderr": True,
            "extract_flat": True,
        }) as dl:
            try:
                for video in dl.extract_info(url, download=False)["entries"]: # type: ignore
                    urls.append(video["url"])
            except Exception as err:
                pass

        return urls
    
    def _get_id_from_url(self, url: str) -> str:
        return url.split("?v=")[1] if "youtube.com" in url else url.split("youtu.be/")[1]

    def _download(self):
        dl_list: list[str] = []

        queue_urls: list[str] = self._urls.copy()
        self._urls = []

        for url in queue_urls:
            id: str = self._get_id_from_url(url)
            file_name: str = f"{id}.m4a"
            file_path: str = os.path.join(self._path, file_name)

            if not self._check_exist(file_path):
                print(f"[i] Queueing {id}")
                dl_list.append(url)
            else:
                self._post_hook(file_path)

        if not dl_list:
            return
        
        self._busy = True

        options = {
            "format": "m4a/bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }],
            "paths": {
                "home": self._path,
            },
            "post_hooks": [self._post_hook],
            "outtmpl": f"%(id)s.%(ext)s",
            "progress_hooks": [self._download_progress],
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "download_archive": self._config.storage.archive,
            "break_on_existing": True,
            # "ignoreerrors": True,
            "break_per_url": True,
            "logtostderr": True,
        }

        if self._config.server.ffmpeg:
            options["ffmpeg_location"] = self._config.server.ffmpeg,

        with yt_dlp.YoutubeDL(options) as dl: # type: ignore
            try:
                dl.download(dl_list)
            except ExtractorError as err:
                pass
            except DownloadError as err:
                print(err)
                id: str = str(err).split(" ")[2]
                print(f"[!] Download Error. Skipping {id}")

                self._lock.acquire()

                to_del: dict[str, str] = {}

                for item in self._requestors:
                    if item["id"] == id:
                        to_del = item
                        break

                if to_del:
                    self._requestors.remove(to_del)

                self._lock.release()
            except Exception as err:
                pass

        self._busy = False

        print(f"[i] Downloads Finished")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1)

            message: str = f"UPDATE|Queue updated"
            sock.sendto(str.encode(message), ("255.255.255.255", self._config.client.port))

        return