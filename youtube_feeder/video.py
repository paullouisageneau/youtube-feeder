
import youtube_dl

from datetime import datetime


class Video:
    def __init__(self, info):
        self.info = info
        self.title = info.get("title", "unknown")
        self.description = info.get("description", "")
        self.duration = int(info.get("duration", "0"))
        self.uploader = info.get("uploader", "unknown")
        self.author = self.uploader

        uldate = info.get("upload_date", None)
        if uldate:
            self.date = datetime(int(uldate[0:4]), int(uldate[4:6]), int(uldate[6:8]))
        else:
            self.date = datetime.now()

        formats = [f for f in self.info.get("formats", []) if "url" in f]
        self.url = formats[-1]["url"] if len(formats) > 0 else None

    def __eq__(self, other):
        return self.date == other.date

    def __lt__(self, other):
        return self.date < other.date

    def __gt__(self, other):
        return self.date > other.date
