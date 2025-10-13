import vlc


class VideoPlayer:
    def __init__(self, video_path: str):
        self.instance = vlc.Instance()
        self.media = self.instance.media_new(video_path)
        self.player = self.instance.media_player_new()
        self.player.set_media(self.media)

    def play(self):
        self.player.play()

    def set_position(self, percent: float):
        self.player.set_position(percent)

    def get_duration(self) -> int:
        return self.player.get_length()
