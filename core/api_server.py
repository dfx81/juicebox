import json

from werkzeug.datastructures import Authorization
from core.downloader import Downloader
from flask import Flask, request
from waitress import serve
from flask_httpauth import HTTPBasicAuth
from threading import Thread

from core.config import Config
from core.player import Player
from core.utils import get_app_version

class ApiServer:
    def __init__(self, config: Config):
        self._config: Config = config
        
        try:
            self._setup()
        except NameError as err:
            raise NameError("VLC not installed")

    def _setup(self):
        self._player: Player = Player()
        self._downloader: Downloader = Downloader(config=self._config, player=self._player)
        self._auth = HTTPBasicAuth()
        self._app = Flask(self._config.server.name)

        @self._auth.verify_password
        def verify(username: str, password: str):
            if self._config.security.password == password and username != "":
                return username
            
            return None

        @self._app.get("/")
        @self._auth.login_required
        def home():
            return {
                "name": self._config.server.name,
                "version": get_app_version(),
                "motd": self._config.motd
            }
        
        @self._app.post("/queue")
        @self._auth.login_required
        def queue_song():
            url: str = request.args["url"]

            creds: Authorization

            if request.authorization:
                creds = request.authorization

            Thread(target=self._queue, args=[url, creds.parameters["username"]]).start()
            
            return {
                "status": "OK",
                "message": "Queued"
            }
        
        @self._app.post("/skip")
        @self._auth.login_required
        def skip_song():
            success: bool = self._player.skip()

            print(f"[i] {"Skipped current song" if success else "No songs in queue to skip"}")

            return {
                "status": "OK",
                "message": "Skipped" if success else "No more songs in queue"
            }
        
        @self._app.get("/list")
        @self._auth.login_required
        def list_queue():
            playlist: list[dict] = self._player.get_queue()

            queue: list[dict] = []

            for item in playlist:
                with open(f"{self._config.storage.downloads}{os.sep}{item["path"].split(".")[0]}.json") as file:
                    data: dict = json.load(file)
                    data["requestor"] = item["requestor"]
                    queue.append(data)

            print(f"[i] Queue requested")

            return {
                "status": "OK",
                "queue": queue
            }
        
    def _queue(self, url: str, requestor: str):
        urls: list[str] = []

        if "playlist?list=" in url:
            urls = self._downloader.get_urls_in_playlist(url)
        else:
            urls = [url]

        for link in urls:
            Thread(target=self._downloader.queue, args=[link, requestor]).start()
    
    def start(self):
        print("[i] API server listening on %s:%d" % (self._config.server.address, self._config.server.port))
        serve(self._app, host=self._config.server.address, port=self._config.server.port, _quiet=True)