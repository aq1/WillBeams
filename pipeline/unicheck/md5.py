import hashlib


def check_key(kv, md5):
    return kv.get(md5) is not None


def put_key(kv, key):
    kv.put(key, b'')


def compute_key(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not len(chunk):
                break
            m.update(chunk)
    return m.digest()
