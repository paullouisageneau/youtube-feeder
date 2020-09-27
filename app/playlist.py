
from .collection import Collection

import random

class Playlist:
    def __init__(self, id):
        self.id = id
        self.collection = Collection(id)
        self.urls = {}


    def add(self, url, name):
        self.urls[url] = name


    def delete(self, url):
        del self.urls[url]


    def fetch(self, conn, url, name):
        self.add(url, name)
        self.collection.fetch(conn, self.id, url)


    def refresh(self, conn):
        for url in self.urls.keys():
            self.collection.fetch(conn, self.id, url)


    def clear(self):
        self.collection.clear()
        self.urls = {}


    def generate_m3u8(self, base_url="", randomized=False):
        if randomized:
             collection = [v for v in self.collection]
             random.shuffle(collection)
        else:
             collection = self.collection

        yield "#EXTM3U\r\n"
        for video in collection:
            title = video.title.replace("-", ":").replace(",", ":")
            author = video.author.replace("-", ":").replace(",", ":")
            yield "#EXTINF:{}, {} - {}\r\n".format(video.duration, author, title)
            yield "{}/video/{}\r\n".format(base_url, video.id)


    def __iter__(self):
        return self.collection.__iter__()


    def __next__(self):
        return self.collection.__next__()


    def save_to_db(self, conn):
        self.collection.save_to_db(conn)

        for url, name in self.urls.items():
            conn.execute("DELETE FROM urls WHERE playlist_id=? ", (self.id,))

        for url, name in self.urls.items():
            conn.execute(
                ("INSERT OR REPLACE INTO urls (playlist_id, url, name) "
                    "VALUES (?, ?, ?)"),
                (self.id, url, name))

        conn.commit()

    @staticmethod
    def load_from_db(conn, id):
        playlist = Playlist(id)
        playlist.collection = Collection.load_from_db(conn, id)

        rows = conn.execute("SELECT url, name FROM urls WHERE playlist_id=?", (id,)).fetchall()
        for r in rows:
            url, name = r
            playlist.add(url, name)

        return playlist


    @staticmethod
    def init_db(conn):
        conn.execute(
            ("CREATE TABLE IF NOT EXISTS urls ( "
                "playlist_id TEXT NOT NULL, "
                "url TEXT NOT NULL, "
                "name TEXT)"))
        conn.execute(
            ("CREATE UNIQUE INDEX IF NOT EXISTS playlist_url "
                "ON urls (playlist_id, url)"))
        conn.commit()


    @staticmethod
    def load_from_file(conn, id, filename):
        playlist = Playlist(id)
        with open(filename, "r") as f:
            name = "Unknown"
            for line in f.readlines():
                line = line.strip()
                if line:
                    if line[0] == "#":
                        name = line[1:].strip()
                    else:
                        playlist.fetch(conn, line.strip(), name)

        return playlist

