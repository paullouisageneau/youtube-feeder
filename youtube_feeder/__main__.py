
from .playlist import Playlist
from .player import Player


playlist = Playlist()
playlist.load("playlist.txt")
playlist.save_m3u8("playlist.m3u8");

#player = Player()
#for video in playlist:
#    print(video.title)
#    print(video.description)
#    player.play(video.url)

