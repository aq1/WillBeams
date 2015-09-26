# import time


# while True:
with open('log.txt', 'r') as f:
    webms = []
    md5s = []
    for i, line in enumerate(f.readlines(), 1):
        a = line.split(';')
        t, w, m = line.split(';')
        webms.append(w)
        md5s.append(m)

    labels = 'urls', 'webms', 'md5'
    data = i, len(set(webms)), len(set(md5s))
    for l, q in zip(labels, data):
        print('%s: %s' % (l, q))

    # time.sleep(10)
