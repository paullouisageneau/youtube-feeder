
import youtube_dl

from .video import Video
from heapq import merge

cache = {}


class Collection:
    def __init__(self, videos=[]):
        self.videos = sorted(videos)

    def fetch(self, url):
        new_videos = Collection.from_url(url)
        self.videos = list(merge(self.videos, new_videos))

    def clear(self):
        self.videos = []

    def __iter__(self):
        return self.videos.__iter__()

    def __next__(self):
        return self.videos.__next__()

    @staticmethod
    def from_url(url):
        try:
            ydl_opts = {
                'ignoreerrors': True,
                'format': '[height <=? 720]',
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False, process=False)
                return Collection.from_info(ydl, info)
        except Exception as e:
            print(repr(e))
            return Collection()

    @staticmethod
    def from_info(ydl, info):
        try:
            if "entries" in info:
                videos = []
                for entry in info["entries"]:
                    c = Collection.from_info(ydl, entry)
                    videos += c.videos
                return Collection(videos)
            else:
                global cache
                video_id = info.get("ie_key", "") + "_" + info["id"]
                if video_id not in cache:
                    info = ydl.process_ie_result(info, download=False, extra_info={})
                    cache[video_id] = Video(info)
                return Collection([cache[video_id]])
        except Exception as e:
            print(repr(e))
            return Collection()
