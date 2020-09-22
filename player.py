#!/usr/bin/env python3

import sys
import subprocess

from urllib.request import urlopen


def iterate_m3u8(url, callback):
    m3u8 = []
    with urlopen(url) as file:
        m3u8 = file.readlines()

    name = "Unknown"
    for line in m3u8:
        line = line.decode('utf-8').strip()
        if line:
            if line[0] == '#':
                if line.startswith("#EXTINF:"):
                    name = line[8:0]
            else:
                callback(line, name)


def main():
    if len(sys.argv) < 3:
        print("Usage: {} URL COMMAND".format(sys.argv[0]))
        sys.exit(-1)

    def play(url, name):
        print(name)
        subprocess.call(sys.argv[2:] + [url], stdout=subprocess.DEVNULL)

    iterate_m3u8(sys.argv[1], play)
    sys.exit(0)


if __name__ == "__main__":
    main()
