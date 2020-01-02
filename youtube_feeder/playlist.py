
from .collection import Collection


class Playlist:
    def __init__(self, filename=None):
        self.collection = Collection()
        self.urls = set()
        if filename:
            self.load(filename)

    def add(self, url):
        self.collection.fetch(url)
        self.urls.add(url)

    def clear(self):
        self.collection.clear()
        self.urls = []

    def refresh(self):
        self.collection.clear()
        for url in self.urls:
            self.collection.fetch(url)

    def load(self, filename):
        with open(filename, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line and line[0] != "#":
                    self.add(line.strip())

    def save_m3u8(self, filename):
        with open(filename, "w") as f:
            f.write("#EXTM3U\r\n")
            for video in self.collection:
                if video.url:
                    title = video.title.replace("-", ":").replace(",", ":")
                    author = video.author.replace("-", ":").replace(",", ":")
                    f.write("#EXTINF:{}, {} - {}\r\n".format(video.duration, author, title))
                    f.write("{}\r\n".format(video.url))

    def __iter__(self):
        return self.collection.__iter__()

    def __next__(self):
        return self.collection.__next__()
