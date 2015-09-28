import os

import scraper


def get_stats():
    for log_file in os.listdir(scraper.LOGS_FOLDER):
        with open(os.path.join(scraper.LOGS_FOLDER, log_file), 'r') as f:
            webms = []
            md5s = []
            for i, line in enumerate(f.readlines(), 1):
                try:
                    t, w, m = line.split(';')
                except ValueError:
                    continue

                webms.append(w)
                md5s.append(m)

            labels = 'urls', 'webms', 'md5'
            data = i, len(set(webms)), len(set(md5s))

            print('%s:' % log_file)
            for l, q in zip(labels, data):
                print('%s: %s' % (l, q))


if __name__ == '__main__':
    get_stats()
