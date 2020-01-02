
import youtube_dl

from .video import Video
from heapq import merge


class Collection:
    def __init__(self, videos=[]):
        self.videos = sorted(videos)

    def fetch(self, url):
        try:
            ydl_opts = {
                'ignoreerrors': True,
                'format': '[height <=? 720]',
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            new_videos = Collection.from_youtube_dl(info)
            self.videos = list(merge(self.videos, new_videos))

        except Exception as e:
            print(repr(e))

    def clear(self):
        self.videos = []

    def __iter__(self):
        return self.videos.__iter__()

    def __next__(self):
        return self.videos.__next__()

    @staticmethod
    def from_youtube_dl(info):
        result = []
        try:
            if "entries" in info:
                for entry in info["entries"]:
                    result += Collection.from_youtube_dl(entry)
            else:
                v = Video(info)
                result.append(v)

        except Exception as e:
            print(repr(e))

        return Collection(result)
