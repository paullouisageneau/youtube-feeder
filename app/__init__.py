
from gevent import monkey

monkey.patch_all()

import flask
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
app.config.from_object("config")

# Connect database
conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row

Video.init_db(conn)
Collection.init_db(conn)
Playlist.init_db(conn)


def url_base(urlpath = ""):
    return app.config["BASE_PATH"] + urlpath


def url_for(*args, **kwargs):
    return url_base(flask.url_for(*args, **kwargs))


def url_absolute(relative_url):
    return app.config["PREFERRED_URL_SCHEME"] + "://" + request.host + relative_url


def url_quote(path):
    return urllib.parse.quote(path)


@app.context_processor
def inject():
    return dict(url_for=url_for, url_quote=url_quote)


# ----- Routes definition -----

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        id = request.form["playlist"]
        return redirect(url_for("playlist_edit", id=id), code=303)
    else:
        return render_template("index.html")


@app.route("/playlist/<id>/edit", methods=["GET", "POST"])
def playlist_edit(id):
    pl = Playlist.load_from_db(conn, id)
    if request.method == "POST":
        action = request.form["action"]
        if action == "create":
             name = request.form["name"]
             url = request.form["url"]
             if name and url:
                 pl.add(url, name)
                 pl.save_to_db(conn)
                 return redirect(url_for("playlist_edit", id=id), code=303)
        elif action == "delete":
            url = request.form["url"]
            if url:
                pl.delete(url)
                pl.save_to_db(conn)
                return redirect(url_for("playlist_edit", id=id), code=303)
        return abort(400)
    else:
        urls = sorted(pl.urls.items(), key=lambda item: item[1])
        return render_template("playlist_edit.html", playlist=pl, urls=urls)


@app.route("/playlist/<id>/view")
def playlist_view(id):
    pl = Playlist.load_from_db(conn, id)
    return render_template("playlist_view.html", playlist=pl)


@app.route("/playlist/<id>/refresh", methods=["GET", "POST"])
def playlist_refresh(id):
    pl = Playlist.load_from_db(conn, id)
    if request.method == "POST":
        pl.refresh(conn)
        pl.save_to_db(conn)
        return redirect(url_for("playlist_view", id=id), code=303)
    else:
        return render_template("refresh.html")


@app.route("/playlist/<id>")
def playlist(id):
    randomized = request.args.get("random", default=False, type=bool)
    pl = Playlist.load_from_db(conn, id)
    return Response(pl.generate_m3u8(url_absolute(url_base()), randomized),
        mimetype="audio/mpegurl",
        headers={"Content-disposition": "attachment; filename={}".format(id + ".m3u8")})


@app.route("/video/<id>")
def get_video(id):
    v = Video.load_from_db(conn, id)
    if not v:
        return abort(404)
    return redirect(Collection.get_video_url(v), code=302)
