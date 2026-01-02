from flask import Flask, request
from waitress import serve
from flask_httpauth import HTTPBasicAuth

from core.config import Config
from core.utils import get_app_version

class ApiServer:
    def __init__(self, config: Config):
        self.config: Config = config
        self._setup()

    def _setup(self):
        self.auth = HTTPBasicAuth()
        self.app = Flask(self.config.server.name)

        @self.auth.verify_password
        def verify(username, password):
            if self.config.security.password == password:
                return username
            
            return None

        @self.app.get("/")
        def home():
            return {
                "name": self.config.server.name,
                "version": get_app_version(),
                "motd": self.config.motd
            }
        
        @self.app.post("/queue")
        @self.auth.login_required
        def queue_song():
            url: str = request.args["url"]
            
            return {}
    
    def start(self):
        print("[i] API server listening on %s:%d" % (self.config.server.address, self.config.server.port))
        serve(self.app, host=self.config.server.address, port=self.config.server.port, _quiet=True)