import os
import json
import yt_dlp

from core.config import Config

class Downloader:
    def __init__(self, config: Config):
        self._config: Config = config
        self._setup()
    
    def _setup(self):
        self._path: str = self._config.storage.downloads
        os.makedirs(self._path, exist_ok=True)
        self._urls: list[str] = []
        self._busy: bool = False

    def queue(self, url: str):
        self._urls.append(url)

        if not self._busy:
            while self._urls:
                self._download()

    def _download_progress(self, info: dict):
        if info["status"] == "finished":
            print(f"[i] Finished Downloading {info["info_dict"]["id"]}")
            with open(f"{self._path}/{info["info_dict"]["id"]}.json", "w", encoding="utf-8") as file:
                json.dump(info["info_dict"], file, ensure_ascii=False, indent=4)

    def _post_hook(self, name: str):
        print(f"[i] Finished Processing {name}")

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
            "ignoreerrors": True,
            "extract_flat": True,
        }) as dl:
            for video in dl.extract_info(url, download=False)["entries"]: # type: ignore
                urls.append(video["url"])

        return urls

    def _download(self):
        dl_list: list[str] = []

        queue_urls: list[str] = self._urls.copy()
        self._urls = []

        for url in queue_urls:
            id: str = url.split("?v=")[1]
            file_name: str = f"{id}.m4a"
            file_path: str = os.path.join(self._path, file_name)

            if not self._check_exist(file_path):
                print(f"[i] Queueing {id}")
                dl_list.append(url)
            else:
                print(f"[i] Skipping {id}")

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
            "ignoreerrors": True,
            "outtmpl": f"%(id)s.%(ext)s",
            "progress_hooks": [self._download_progress],
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "download_archive": self._config.storage.archive,
            "break_on_existing": True,
            "break_per_url": True,
            "logtostderr": True,
        }

        with yt_dlp.YoutubeDL(options) as dl: # type: ignore
            dl.download(dl_list)

        self._busy = False

        print(f"[i] Downloads Finished")
        return