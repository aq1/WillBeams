import hashlib


PREFIX = b'md5:'


def compute_key(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not len(chunk):
                break
            m.update(chunk)
    return m.digest()
