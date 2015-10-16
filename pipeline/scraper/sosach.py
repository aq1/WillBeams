# usage:
# python -m pipeline.scraper.sosach --boards pr
import requests
import argparse
import json
import pickle
from pipeline.rabbit import simple_putter, rabbit_main
from pipeline.unicheck import UnicheckClient
from pipeline.config import DOWNLOADER_QUEUE_NAME
from pipeline.unicheck.md5 import PREFIX as md5_PREFIX
from time import sleep
from random import random


parser = argparse.ArgumentParser()
parser.add_argument('--boards', nargs='*', default=[], help='List of boards to parse')

BOARDS = {
    'a', 'abu', 'au', 'b', 'bg', 'bi', 'biz', 'bo', 'c', 'cg', 'd', 'di', 'diy', 'e', 'em', 'es',
    'fa', 'fag', 'fd', 'fet', 'fg', 'fiz', 'fl', 'ftb', 'fur', 'ga', 'gd', 'gg', 'h', 'hc',
    'hh', 'hi', 'ho', 'hw', 'ja', 'ma', 'me', 'media', 'mg', 'mlp', 'mmo', 'mo', 'moba',
    'mobi', 'mov', 'mu', 'mus', 'ne', 'p', 'pa', 'po', 'pr', 'psy', 'r', 'ra', 're', 'rf', 's',
    'sci', 'sex', 'sf', 'sn', 'soc', 'sp', 'spc', 't', 'tes', 'trv', 'tv', 'un', 'vg', 'vn', 'w',
    'web', 'wh', 'wm', 'wn', 'wp', 'wr', 'wrk'
}

NSFW_BOARDS = {
    'fg', 'fur', 'gg', 'ga', 'h', 'ho', 'hc', 'e', 'fet', 'sex', 'fag'
}

WEBM_TYPE = 6


session = requests.Session()


def _get_json(url, can_skip=False):
    sleep(3 + random() * 5)
    r = session.get(url)
    if can_skip and r.status_code != 200:
        return None
    assert r.status_code == 200, 'Bad HTTP status {}'.format(r.status_code)
    return json.loads(r.text)


def add_webms(batch, board_tick, *, output, unicheck):
    md5_map = {md5_PREFIX + md5: url for url, md5 in batch}
    res = unicheck.call('check', set(md5_map.keys()))
    accepted = set()
    for k, v in res.items():
        if v is None:
            accepted.add(md5_map[k])
    print('Amount of webms: {} ({} rejected + {} enqueued)'.format(
        len(batch), len(batch) - len(accepted), len(accepted)
    ))
    for url in accepted:
        output(
            url,
            nsfw=board_tick in NSFW_BOARDS,
            tags=[board_tick]
        )


def parse_thread(board_tick, thread_num, *, output, unicheck):
    print('Parsing thread /{}/res/{}.json'.format(board_tick, thread_num))
    url = 'http://2ch.hk/{}/res/{}.json'.format(board_tick, thread_num)
    thread = _get_json(url, can_skip=True)
    if thread is None:
        print('Skip')
        return
    batch = []
    for post in thread['threads'][0]['posts']:
        for f in post.get('files', []):
            if f['type'] != WEBM_TYPE:
                continue
            batch.append((
                'http://2ch.hk/{}/{}'.format(board_tick, f['path']),
                bytes.fromhex(f['md5']),
            ))
    add_webms(batch, board_tick, output=output, unicheck=unicheck)


def parse_board(board_tick, *, output, unicheck):
    print('Parsing board /{}/'.format(board_tick))
    url = 'http://2ch.hk/{}/catalog.json'.format(board_tick)
    board = _get_json(url)
    for thread_info in board['threads']:
        if not int(thread_info['files_count']):
            continue
        parse_thread(board_tick, thread_info['num'], output=output, unicheck=unicheck)


def serialize_req(url, **kw):
    d = {'url': url}
    d.update(kw)
    return pickle.dumps(d)


@rabbit_main
def main(connection):
    args = parser.parse_args()
    uniq = UnicheckClient(connection)
    output = simple_putter(connection, serialize_req, queue_name=DOWNLOADER_QUEUE_NAME)
    for board in args.boards:
        parse_board(board, output=output, unicheck=uniq)


if __name__ == '__main__':
    main()
