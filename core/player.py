import socket
import vlc
from threading import Thread

from core.config import Config

class Player:
    def __init__(self, config: Config):
        self._config: Config = config
        self._setup()

    def _setup(self):
        self._instance: vlc.Instance = vlc.Instance() # type: ignore
        self._player: vlc.MediaListPlayer = self._instance.media_list_player_new()

        self._playlist: vlc.MediaList = self._instance.media_list_new()
        self._player.set_media_list(self._playlist)
        self._requestors: list[str] = []

        event_manager: vlc.EventManager = self._player.get_media_player().event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self._media_changed) # type: ignore

    def _media_changed(self, event: vlc.Event):
        player: vlc.MediaPlayer = self._player.get_media_player()
        current: vlc.Media = player.get_media()
        player.release()
        idx: int = self._playlist.index_of_item(current)

        print(f"[i] Playing {current.get_mrl().split("/")[-1].split(".")[0]}. Requested by {self._requestors[idx]}")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1)

            message: str = f"UPDATE|Queue updated"
            sock.sendto(str.encode(message), ("255.255.255.255", self._config.client.port))

    def queue(self, file: str, requestor: str):
        media: vlc.Media = self._instance.media_new(file)
        
        if not self._player.is_playing():
            self._requestors = []
            self._playlist = self._instance.media_list_new()
            self._player.set_media_list(self._playlist)

        self._playlist.lock()
        self._playlist.add_media(media)
        self._requestors.append(requestor)
        self._playlist.unlock()

        if not self._player.is_playing():
            self._play()

    def _play(self):
        if self._player.is_playing():
            return

        self._player.next()

    def _play_next(self):
            self._player.next()
    
    def skip(self) -> bool:
        if self._player.is_playing():
            err: int = self._player.next()

            if err == -1:
                self._player.stop()
                self._playlist = self._instance.media_list_new()
                self._requestors = []
                self._player.set_media_list(self._playlist)

            return True
        
        return False
    
    def get_queue(self) -> list[dict]:
        player: vlc.MediaPlayer = self._player.get_media_player()
        current: vlc.Media = player.get_media()

        idx: int = self._playlist.index_of_item(current)
        self._playlist.lock()
        total: int = self._playlist.count()
        self._playlist.unlock()

        queue: list[dict] = []

        if idx < 0:
            return queue

        for i in range(idx, total):
            self._playlist.lock()
            media: vlc.Media = self._playlist.item_at_index(i)
            self._playlist.unlock()
            path: str = media.get_mrl()
            queue.append({
                "requestor": self._requestors[i],
                "path": path.split("/")[-1]
            })

        return queue