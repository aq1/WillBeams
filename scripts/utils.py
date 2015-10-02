import os
import sys
import collections
import shutil

import scraper

import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'WillBeams'))
sys.path.append(BASE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = 'WillBeams.settings'
django.setup()

from webm.models import Webm


def get_stats():
    for log_file in os.listdir(scraper.LOGS_FOLDER):
        try:
            with open(os.path.join(scraper.LOGS_FOLDER, log_file), 'r') as f:
                webms = []
                md5s = []
                for i, line in enumerate(f.readlines(), 1):
                    try:
                        w, t, m = line.split(';')
                    except ValueError:
                        continue

                    webms.append(w)
                    md5s.append(m)

                labels = 'urls', 'webms', 'md5'
                data = i, len(set(webms)), len(set(md5s))

                print('%s:' % log_file)
                for l, q in zip(labels, data):
                    print('%s: %s' % (l, q))
        except Exception as e:
            print(e)
            continue


def sort_webms_by_md5():
    for log_file in os.listdir(scraper.LOGS_FOLDER):
        with open(os.path.join(scraper.LOGS_FOLDER, log_file), 'r') as f:
            md5s = collections.defaultdict(list)
            for i, line in enumerate(f.readlines(), 1):
                try:
                    w, t, m = line[:-1].split(';')
                except ValueError:
                    continue
                md5s[m].append(t)
            for k, v in md5s.items():
                print('{}\t{}'.format(k, '\n\t'.join(map(str, v))))


def delete_all_webms():
    confirm = input('Really? Y/N ')

    if confirm not in ('y', 'Y', 'yes', 'yeap', 'da', 'aga', 'konechno', 'go'):
        print('Didn\'t do anything.')
        exit()

    Webm.objects.all().delete()


def count_webms():
    print(Webm.objects.count())


def clear_working_dir():
    delete_all_webms()
    project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    for d in ('scripts/logs', 'WillBeams/media'):
        path = os.path.join(project_dir, d)
        if os.path.exists(path):
            shutil.rmtree(path)


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        func = globals().get(arg, None)
        if func:
            func()
