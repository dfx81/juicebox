import socket

from core.config import Config
from core.models.payload import Payload
from core.models.request_type import RequestType

class DiscoveryServer:
    def __init__(self, config: Config):
        self.config: Config = config

        self._setup()

    def _setup(self):
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.config.server.address, self.config.server.port))

    def start(self):
        print("[i] Discovery server listening on %s:%d" % (self.config.server.address, self.config.server.port))

        while True:
            packet, address = self.socket.recvfrom(512)
            print("[<] Received payload from %s" % str(address))
            payload: Payload = Payload(packet.decode())

            if (payload.request == RequestType.DISCOVER and payload.arguments == self.config.server.name):
                message: str = "FOUND|%s" % self.config.server.name
                print("[>] Replying to request from %s" % str(address))
                self.socket.sendto(message.encode(), address)
            else:
                print("[i] Ignoring request from %s" % str(address))