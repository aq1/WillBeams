from WillBeams.addvideo import add_prepared_video
from .videoproc.ff import get_file_info, generate_thumbs
from .rabbit import simple_getter, rabbit_main
from .config import DOWNLOADER_QUEUE_NAME, THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH, THUMBNAIL_RATIO
import pickle
import requests
from tempfile import TemporaryDirectory
from os.path import join
from pipeline.unicheck.md5 import compute_key as md5_compute_key, PREFIX as md5_PREFIX
from pipeline.unicheck import UnicheckClient
from time import sleep


def get_ff_filter(width, height):
    result = []
    if width > height * THUMBNAIL_RATIO:
        # constant height
        result.append('scale={}:{}'.format(-1, THUMBNAIL_HEIGHT))
    else:
        # constant width
        result.append('scale={}:{}'.format(THUMBNAIL_WIDTH, -1))
    result.append('crop=w={}:h={}'.format(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
    return ', '.join(result)


def add_video(video_filename, thumbdir, **kwargs):
    ffinfo = get_file_info(video_filename)
    filt = get_ff_filter(ffinfo.width, ffinfo.height)
    thumbs = generate_thumbs(ffinfo, thumbdir, minstep=20, count=5, vfilters=filt)
    add_prepared_video(
        ffinfo,
        thumbs=thumbs,
        **kwargs
    )


def compute_keys(video_filename):
    return {
        md5_PREFIX: md5_PREFIX + md5_compute_key(video_filename),
    }


def check_uniqueness(uniq, keys):
    # returns True if video is unique and can be passed further
    res = uniq.call('check', {keys[md5_PREFIX]})
    return res[keys[md5_PREFIX]] is None


def put_keys(uniq, keys):
    uniq.call('put', {v: b'' for v in keys.values()})


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


def handler(uniq, url, *, nsfw=False, tags=None, md5=None):
    pre_md5_key = None
    if md5 is not None:
        # additional pre-downloading check
        pre_md5_key = md5_PREFIX + md5
        r = uniq.call('check', {pre_md5_key})
        if r[pre_md5_key] is not None:
            print('skip')
            return True

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
        print('downloaded into {}'.format(video_filename))
        keys = compute_keys(video_filename)

        if pre_md5_key is not None and keys[md5_PREFIX] != pre_md5_key:
            print('! md5 keys not matching: {} != {}'.format(pre_md5_key, keys[md5_PREFIX]))

        if not check_uniqueness(uniq, keys):
            print('rejected')
            return True  # not unique, ignore
        print('accepted')
        add_video(video_filename, dir_name, nsfw_source=nsfw, tags=tags)
        put_keys(uniq, keys)
        print('added')
        return True


@rabbit_main
def main(connection):
    uniq = UnicheckClient(connection)

    def inner_handler(*args, **kwargs):
        return handler(uniq, *args, **kwargs)

    simple_getter(connection, deserialize_msg, inner_handler, queue_name=DOWNLOADER_QUEUE_NAME, no_ack=False)
