
from datetime import datetime


class Video:
    def __init__(self, id, info):
        self.id = id
        self.url = info["url"]
        self.title = info.get("title", "unknown")
        self.description = info.get("description", "")
        self.duration = info.get("duration", "0")
        self.uploader = info.get("uploader", "unknown")

        date = info.get("upload_date", None)
        if isinstance(date, datetime):
            self.upload_date = date
        elif isinstance(date, str):
            self.upload_date = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
        else:
            self.upload_date = datetime.now()

        self.author = self.uploader
        self.date = self.upload_date


    def save_to_db(self, conn):
        conn.execute(
            ("INSERT OR REPLACE INTO videos (id, url, title, description, duration, uploader, upload_timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)"),
            (self.id,
                self.url,
                self.title,
                self.description,
                self.duration,
                self.uploader,
                datetime.timestamp(self.upload_date)))
        conn.commit()


    @staticmethod
    def load_from_db(conn, video_id):
        row = conn.execute("SELECT * FROM videos WHERE id=?", (video_id,)).fetchone()
        if not row:
            return None
        info = dict(row)
        info["upload_date"] = datetime.fromtimestamp(info["upload_timestamp"])
        return Video(info["id"], info)


    @staticmethod
    def init_db(conn):
        conn.execute(
            ("CREATE TABLE IF NOT EXISTS videos ( "
                "id TEXT PRIMARY KEY, "
                "url TEXT NOT NULL, "
                "title TEXT NOT NULL, "
                "description TEXT NOT NULL, "
                "duration INT NOT NULL, "
                "uploader TEXT NOT NULL, "
                "upload_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
        conn.commit()


    def __eq__(self, other):
        if isinstance(other, Video):
            return self.id == other.id
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, Video):
            return self.date > other.date
        else:
            return False


    def __gt__(self, other):
        if isinstance(other, Video):
            return self.date < other.date
        else:
            return False
