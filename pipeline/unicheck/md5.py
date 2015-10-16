import hashlib


PREFIX = b'md5:'


def check_keys(kv, keys):
    r = kv.get_many({PREFIX + k for k in keys})
    return {k[len(PREFIX):]: v for k, v in r.items()}


def put_keys(kv, d):
    kv.put_many({PREFIX + k: v for k, v in d.items()})
    return True


def compute_key(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not len(chunk):
                break
            m.update(chunk)
    return m.digest()
