import socket
import requests

from requests.auth import HTTPBasicAuth
from core.config import Config


class Client:
    def __init__(self, config: Config):
        self._config: Config = config
        self._setup()

    def __del__(self):
        if self._socket:
            self._socket.close()

    def _setup(self):
        self._connected: bool = False
        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._socket.settimeout(1)

    def find(self, name: str = "") -> list[tuple]:
        candidates: list[tuple] = []

        message: str = f"DISCOVERY|{name}"
        self._socket.sendto(str.encode(message), ("255.255.255.255", self._config.server.port))

        for i in range(self._config.client.discovery_period):
            try:
                _, addr = self._socket.recvfrom(512)
                candidates.append((addr[0], addr[1]))
            except TimeoutError:
                pass

        return candidates
    
    def connect(self, name: str, password: str = "", address: tuple = ("127.0.0.1", 8181)) -> str:
        self._address: tuple = address
        self._name: str = name
        self._password: str = password

        response: requests.Response = requests.get(f"http://{self._address[0]}:{self._address[1]}", auth=HTTPBasicAuth(self._name, self._password))

        self._connected = response.ok

        return response.json()["motd"] if self._connected else "Unauthorized"

    def disconnect(self) -> bool:
        self._address = tuple()
        self._name = ""
        self._password = ""

        self._connected = False

        return not self._connected

    def queue(self, url: str) -> str:
        if self._connected:
            res: requests.Response = requests.post(f"http://{self._address[0]}:{self._address[1]}/queue?url={url}", auth=HTTPBasicAuth(self._name, self._password))

            return res.json()["message"]
        
        return "Not connected to any Juicebox server."

    def skip(self) -> str:
        if self._connected:
            res: requests.Response = requests.post(f"http://{self._address[0]}:{self._address[1]}/skip", auth=HTTPBasicAuth(self._name, self._password))

            return res.json()["message"]
        
        return "Not connected to any Juicebox server."

    def get_playlist(self) -> list[dict]:
        current_queue: list[dict] = []
        
        if self._connected:
            response: requests.Response = requests.get(f"http://{self._address[0]}:{self._address[1]}/list", auth=HTTPBasicAuth(self._name, self._password))
            current_queue = response.json()["queue"]

        return current_queue