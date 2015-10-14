from sys import argv
from pipeline.unicheck.md5 import compute_key
from pipeline.unicheck import UnicheckClient
from pipeline.rabbit import rabbit_main


print(argv[1])
key = compute_key(argv[1])
print(key)


@rabbit_main
def main(connection, channel):
    uniq = UnicheckClient(connection, channel)
    print(uniq.call('check', 'md5', key))


if __name__ == '__main__':
    main()
