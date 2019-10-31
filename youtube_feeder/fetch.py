
import youtube_dl

from player import Player

url = "https://www.youtube.com/playlist?list=PLJGOq3JclTH_BvAEjsCzTsqGQ9y-3i7yN"


class Video:
    def __init__(self, info):
        self.title = info.get("title", "")
        self.description = info.get("description", "")
        formats = [f for f in info.get("formats", []) if "url" in f]
        if len(formats) == 0:
            raise ValueError("No valid formats for video")
        self.url = formats[-1]["url"]


def make_list(info):
    result = []
    try:
        if "entries" in info:
            for entry in info["entries"]:
                result += make_list(entry)
        else:
            v = Video(info)
            result.append(v)

    except ValueError as e:
        print(repr(e))

    return result


ydl_opts = {
    'format': '[height <=? 720]',
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    lst = make_list(info)

    for v in lst:
        print(v.title)
        print(v.description)
        p = Player()
        p.play(v.url)
        p.wait()
