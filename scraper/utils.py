import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DJANGO_PROJECT_DIR = os.path.join(BASE_DIR, 'WillBeams')

SECTIONS = ['a', 'abu', 'au', 'b', 'bg', 'bi', 'biz', 'bo',
            'c', 'cg', 'd', 'di', 'diy', 'e', 'em', 'es',
            'fa', 'fag', 'fd', 'fet', 'fg', 'fiz', 'fl',
            'ftb', 'fur', 'ga', 'gd', 'gg', 'h', 'hc',
            'hh', 'hi', 'ho', 'hw', 'ja', 'ma', 'me',
            'media', 'mg', 'mlp', 'mmo', 'mo', 'moba',
            'mobi', 'mov', 'mu', 'mus', 'ne', 'p', 'pa',
            'po', 'pr', 'psy', 'r', 'ra', 're', 'rf', 's',
            'sci', 'sex', 'sf', 'sn', 'soc', 'sp', 'spc',
            't', 'tes', 'trv', 'tv', 'un', 'vg', 'vn', 'w',
            'web', 'wh', 'wm', 'wn', 'wp', 'wr', 'wrk']


STOP_SIGNAL = 'Stop there'

INFO, WARNING, ERROR, IMPORTANT_INFO = 3, 2, 1, 1
VERBOSITY_LEVEL = IMPORTANT_INFO
WEBM = 6

BOARD_URL = '2ch.hk'
DEFAULT_SECTIONS = ['b', 'vg']
CATALOG_URL = '/{}/catalog.json'
THREAD_URL = '/{}/res/{}.json'
RESOURCE_URL = '/{}/{}'


PARSERS = 2
DOWNLOADERS = 1
Q_NAME = 'webm'


CONSOLE_COLORS = {
    INFO: '\033[0m',
    WARNING: '\033[93m',
    ERROR: '\033[91m',
    'HEADER': '\033[95m',
    'OKGREEN': '\033[92m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
}


def inform(msg, level=10):

    if level <= VERBOSITY_LEVEL:
        print('{}{}{}'.format(CONSOLE_COLORS[level], msg, CONSOLE_COLORS['ENDC']))


def chunk_list(l, pieces):
    size = len(l) // pieces
    yield from [l[i:i + size] for i in range(0, len(l), size)]
