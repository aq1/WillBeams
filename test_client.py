from sys import argv
from pipeline.unicheck.md5 import compute_key
from pipeline.unicheck import UnicheckClient
from pipeline.rabbit import rabbit_main, simple_putter
from pipeline.config import DOWNLOADER_QUEUE_NAME
import pickle


def test_checker():
    print(argv[1])
    key = compute_key(argv[1])
    print(key)

    @rabbit_main
    def main(connection):
        uniq = UnicheckClient(connection)
        # print(uniq.call('put', 'md5', {key: b''}))
        print(uniq.call('check', 'md5', {key}))

    main()


def test_downloader():
    print(argv[1])

    def serialize(url):
        return pickle.dumps({'url': url})

    @rabbit_main
    def main(connection):
        putter = simple_putter(connection, serialize, queue_name=DOWNLOADER_QUEUE_NAME)
        putter(argv[1])

    main()


if __name__ == '__main__':
    test_checker()
    # test_downloader()
