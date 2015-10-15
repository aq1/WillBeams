from WillBeams.addvideo import add_prepared_video
from videoproc.ff import Webminfo
from .rabbit import simple_getter, rabbit_main
from .config import DOWNLOADER_QUEUE_NAME
import pickle
import requests
from tempfile import TemporaryDirectory
from os.path import join
from pipeline.unicheck.md5 import compute_key as md5_compute_key
from pipeline.unicheck import UnicheckClient
from time import sleep


def add_video(video_filename, **kwargs):
    with Webminfo(video_filename, minstep=20, count=1, width=600, cwidth=400) as winfo:
        thumb = None
        if len(winfo.thumbs):
            thumb = winfo.thumbs[0]
        add_prepared_video(
            video_filename,
            round(winfo.duration),
            preview_filename=thumb,
            **kwargs
        )


def compute_keys(video_filename):
    return {
        'md5': md5_compute_key(video_filename),
    }


def check_uniqueness(uniq, keys):
    # returns True if video is unique and can be passed further
    return not uniq.call('check', 'md5', keys['md5'])


def put_keys(uniq, keys):
    for k, v in keys.items():
        uniq.call('put', k, v)  # TODO: batching


def deserialize_msg(v):
    # typical input:
    # {'url': 'http://...', nsfw: True, tags: {'a', 'b', ...}}
    kw = pickle.loads(v)
    url = kw.pop('url')
    return (url, ), kw


def download_content(r, video_filename):
    with open(video_filename, 'wb') as fd:
        for chunk in r.iter_content(4096):
            fd.write(chunk)


def handler(uniq, url, *, nsfw=False, tags=None):
    sleep(5)  # prevent requesting very fast
    print(url)
    r = requests.get(url)
    print(r.status_code)
    if r.status_code != 200:
        if r.status_code == 404:
            return True  # mark as handled
        return False  # retry later
    with TemporaryDirectory() as dir_name:
        video_filename = join(dir_name, 'video.webm')
        download_content(r, video_filename)
        print(video_filename, 'downloaded')
        keys = compute_keys(video_filename)
        if not check_uniqueness(uniq, keys):
            return True  # not unique, ignore
        add_video(video_filename, nsfw_source=nsfw, tags=tags)
        put_keys(uniq, keys)
        return True


@rabbit_main
def main(connection):
    uniq = UnicheckClient(connection)

    def inner_handler(*args, **kwargs):
        return handler(uniq, *args, **kwargs)

    simple_getter(connection, deserialize_msg, inner_handler, queue_name=DOWNLOADER_QUEUE_NAME)
