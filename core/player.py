import vlc
from threading import Thread

class Player:
    def __init__(self):
        self._instance: vlc.Instance = vlc.Instance() # type: ignore
        self._player: vlc.MediaListPlayer = self._instance.media_list_player_new()
        self._playlist: vlc.MediaList = self._instance.media_list_new()
        self._player.set_media_list(self._playlist)

    def queue(self, file: str):
        media: vlc.Media = self._instance.media_new(file)
        
        if not self._player.is_playing():
            self._playlist = self._instance.media_list_new()
            self._player.set_media_list(self._playlist)

        self._playlist.lock()
        self._playlist.add_media(media)
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
                self._player.set_media_list(self._playlist)

            return err == -1
        
        return False
    
    def get_queue(self) -> list[str]:
        player: vlc.MediaPlayer = self._player.get_media_player()
        current: vlc.Media = player.get_media()

        idx: int = self._playlist.index_of_item(current)
        self._playlist.lock()
        total: int = self._playlist.count()
        self._playlist.unlock()

        queue: list[str] = []

        if idx < 0:
            return queue

        for i in range(idx, total):
            self._playlist.lock()
            media: vlc.Media = self._playlist.item_at_index(i)
            self._playlist.unlock()
            path: str = media.get_mrl()
            queue.append(path.split("/")[-1])

        return queue