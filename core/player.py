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
        self._playing: bool = False
        self._index: int = -1
        self._requestors: list[str] = []
        self._songs: list[str] = []

        event_manager: vlc.EventManager = self._player.get_media_player().event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self._media_changed) # type: ignore
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._play_end) # type: ignore

    def _media_changed(self, event: vlc.Event):
        self._playing = True
        self._index = self._index + 1

        player: vlc.MediaPlayer = self._player.get_media_player()
        current: vlc.Media = player.get_media()
        player.release()

        print(f"[i] Playing {self._songs[self._index]} ({self._index + 1} / {len(self._songs)}). Requested by {self._requestors[self._index]}")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1)

            message: str = f"UPDATE|Queue updated"
            sock.sendto(str.encode(message), ("255.255.255.255", self._config.client.port))

    def _play_end(self, event: vlc.Event):
        print(f"[i] Song ended ({self._index + 1}/{len(self._songs)})")
        
        if self._index + 1 >= len(self._songs):
            print("[i] Playlist ended")

            self._playing = False
            self._requestors = []
            self._index = -1
            self._songs = []
            self._playlist = self._instance.media_list_new()
            self._player.set_media_list(self._playlist)

    def queue(self, file: str, requestor: str):
        media: vlc.Media = self._instance.media_new(file)
        
        if not self._playing:
            self._requestors = []
            self._index = -1
            self._songs = []
            self._playlist = self._instance.media_list_new()
            self._player.set_media_list(self._playlist)

        self._playlist.lock()
        self._playlist.add_media(media)
        self._requestors.append(requestor)
        self._songs.append(file)
        self._playlist.unlock()

        if not self._playing:
            self._play()

    def _play(self):
        if self._playing:
            return
        
        self._player.play()

    def _play_next(self):
        self._player.next()
    
    def skip(self) -> bool:
        if self._playing:
            err: int = self._player.next()

            if err == -1:
                self._player.stop()
                self._index = 0
                self._playing = False
                self._songs = []
                self._playlist = self._instance.media_list_new()
                self._requestors = []
                self._player.set_media_list(self._playlist)

            return True
        
        return False
    
    def get_queue(self) -> list[dict]:
        idx: int = self._index
        total: int = len(self._songs)

        queue: list[dict] = []

        print(f"[i] Queue Info: {idx + 1}/{total}")

        if idx < 0:
            return queue

        for i in range(idx, total):
            path: str = self._songs[idx]
            queue.append({
                "requestor": self._requestors[i],
                "path": self._songs[i]
            })

        return queue