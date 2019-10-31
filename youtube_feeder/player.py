import subprocess

class Player:
    def __init__(self):
        self._proc = None

    def play(self, url):
        self.wait()
        self._proc = subprocess.Popen(
            ["vlc", "--play-and-exit", url],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )

    def wait(self):
        if self._proc and self._proc.poll() is None:
            self._proc.wait()
        self._proc = None

