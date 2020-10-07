
from .video import Video
from heapq import merge

import youtube_dl
import logging

ydl_opts = {
    'ignoreerrors': True,
    'format': '[height <=? 720]',
}
ydl = youtube_dl.YoutubeDL(ydl_opts)


def merge_unique(*iterables):
    last = object()

    for val in merge(*iterables):
        if val != last:
            last = val
            yield val


class Collection:
    def __init__(self, id, videos=[]):
        self.id = id
        self.videos = sorted(videos)


    def fetch(self, conn, id, url):
        c = Collection.from_url(conn, id, url)
        if c:
            self.videos = list(merge_unique(self.videos, c.videos))


    def clear(self):
        self.videos = []


    def __iter__(self):
        return self.videos.__iter__()


    def __next__(self):
        return self.videos.__next__()


    @staticmethod
    def from_url(conn, id, url):
        try:
            info = ydl.extract_info(url, download=False, process=False)
            return Collection.from_info(conn, id, ydl, info)

        except Exception as e:
            logging.exception(e)
            return Collection(id, [])


    @staticmethod
    def from_info(conn, id, ydl, info):
        try:
            if "entries" in info:
                videos = []
                for entry in info["entries"]:
                    c = Collection.from_info(conn, id, ydl, entry)
                    videos += c.videos
                return Collection(id, videos)

            elif "id" in info:
                video_id = info.get("ie_key", "") + '_' + info["id"]
                url = info.get("url", info["id"])
                video = Video.load_from_db(conn, video_id)
                if video is None:
                    info = ydl.process_ie_result(info, download=False, extra_info={})
                    if info is None:
                        return Collection(id, [])
                    info["url"] = url
                    video = Video(video_id, info)
                    video.save_to_db(conn)
                return Collection(id, [video])

            elif "url" in info and "://" in info["url"]:
                return Collection.from_url(conn, id, info["url"])

        except Exception as e:
            logging.exception(e)
            return Collection(id, [])


    def save_to_db(self, conn):
        for video in self.videos:
            conn.execute(
                ("INSERT OR REPLACE INTO collections (id, video_id) "
                    "VALUES (?, ?)"),
                (self.id, video.id))

        conn.commit()

    @staticmethod
    def load_from_db(conn, id):
        rows = conn.execute("SELECT video_id FROM collections WHERE id=?", (id,)).fetchall()
        videos = [Video.load_from_db(conn, r[0]) for r in rows]
        return Collection(id, [v for v in videos if v])


    @staticmethod
    def init_db(conn):
        conn.execute(
            ("CREATE TABLE IF NOT EXISTS collections ( "
                "id TEXT TEXT NOT NULL, "
                "video_id TEXT NOT NULL)"))
        conn.execute(
            ("CREATE UNIQUE INDEX IF NOT EXISTS collection_video "
                "ON collections (id, video_id)"))
        conn.commit()


    @staticmethod
    def get_video_url(video):
        ie_key, id = video.id.split('_', 1)
        info = vars(video)
        info['ie_key'] = ie_key
        info['id'] = id
        info["_type"] = "url"
        info = ydl.process_ie_result(info, download=False, extra_info={})
        return info.get("url", None) if info else None

