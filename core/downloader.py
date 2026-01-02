import os
import yt_dlp

from core.config import Config

class Downloader:
    def __init__(self, config: Config):
        self.path: str = config.storage.downloads
        os.makedirs(self.path, exist_ok=True)

    def download(self, url: str):
        id: str = url.split("?")[1]
        fileName: str = id + ".m4a"
        filePath: str = os.path.join(self.path, fileName)

        if os.path.isfile(filePath):
            return 

        options: dict = {
            "format": "m4a/bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }]
        }

        return