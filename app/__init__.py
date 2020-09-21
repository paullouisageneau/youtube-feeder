
from gevent import monkey

monkey.patch_all()

from flask import (
    Flask,
    request,
    Response,
    redirect,
    abort,
    render_template,
    send_from_directory,
    jsonify,
)

from .playlist import Playlist
from .collection import Collection
from .video import Video

import sqlite3


# ----- App initialization -----

# Create the Flask app
app = Flask(__name__, static_url_path="/static")

# Connect database
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

Video.init_db(conn)
Collection.init_db(conn)
Playlist.init_db(conn)


# ----- Routes definition -----

@app.route("/playlist/<id>")
def get_playlist(id):
    pl = Playlist.load_from_file(conn, id, "playlist.txt")
    pl.save_to_db(conn)
    #pl = Playlist.load_from_db(conn, id)
    return Response(pl.generate_m3u8("http://localhost:8080"), mimetype="audio/mpegurl")


@app.route("/video/<id>")
def get_video(id):
    v = Video.load_from_db(conn, id)
    if not v:
        return abort(404)
    return redirect(Collection.get_video_url(v), code=302)
