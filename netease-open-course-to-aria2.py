#!/usr/bin/env python3
# coding: utf-8

"""
Generate a list of urls for aria2

* Netease open course API
Get playlist in JSON format:
  http://mobile.open.163.com/movie/{plid}/getMoviesForAndroid.htm

http://c.open.163.com/opensg/mopensg.do?uuid=8EFFDA1C-126A-351B-0F47-A7558C9B5FEC&ursid=&count=24
http://c.open.163.com/mobile/recommend/v1.do?mt=iphone
http://c.open.163.com/mobile/recommend/v1.do?mt=
http://open.163.com/special/openclass/nvshenbillboard.html
http://so.open.163.com/movie/MBCP3VMPL/getMovies4Ipad.htm
http://comment.api.163.com/api/json/post/list/hot/video_bbs/BCP6B4MS008535RB/0/10/10/5/2
http://comment.api.163.com/api/json/post/list/normal/video_bbs/BCP6B4MS008535RB/desc/0/10/10/5/2
"""


import logging
import os
import sys

import requests


DATA_DIR = "."
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20120101 Firefox/50.0"
}


def get_urls_in_playlist(plid):
    BASE_URL = "http://mobile.open.163.com/movie/{plid}/getMoviesForAndroid.htm"
    url = BASE_URL.format(plid=plid)
    playlist = requests.get(url).json()

    # English title
    playlist_title = playlist["subtitle"].strip()
    if not playlist_title:
        # Chinese title
        playlist_title = playlist["title"].strip()
    dir_name = f"{plid}.{playlist_title}"
    directory = os.path.join(DATA_DIR, dir_name)

    urls = []
    urls.append((url, directory, "playlist.json"))

    for v in playlist["videoList"]:
        episode = "{:0>2}".format(v["pnumber"])
        # repovideourlOrigin version has no preamble and subtitle
        url = v["repovideourlOrigin"]
        if not url:
            url = v["repovideourl"]
        title = v["title"].strip()
        extension = url.split(".")[-1]
        filename = f"{episode}.{title}.{extension}"
        urls.append((url, directory, filename))

        # subtitles
        for subtitle in v["subList"]:
            url = subtitle["subUrl"]
            language = subtitle["subName"]
            if language == "英文":
                filename = f"{episode}.en.srt"
            elif language == "中文":
                filename = f"{episode}.zh-cn.srt"
            else:
                filename = f"{episode}.{language}.srt"
            urls.append((url, directory, filename))

    return dir_name, urls


def aria2(urls):
    """
    Args:
        url: [{url, directory, filename}, ...]
    """
    template = """{}\n    dir={}\n    out={}\n"""
    rules = [template.format(*i) for i in urls]
    return "\n".join(rules)


def main():
    """Usage:
    main.py [plid]
    """

    logging.basicConfig(level=logging.INFO)

    for plid in sys.argv[1:]:
        logging.info(f"Getting {plid}.")
        title, urls = get_urls_in_playlist(plid)
        aria2_rules = aria2(urls)
        with open(title + ".aria2", "w") as f:
            f.write(aria2_rules)
        logging.info(f"{title} done.")


if __name__ == '__main__':
    main()
