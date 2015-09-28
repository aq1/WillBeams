confirm = input('Really? Y/N ')

if confirm not in ('y', 'Y', 'yes', 'yeap', 'da', 'aga', 'konechno', 'go'):
    print('Didn\'t do anything.')
    exit()

import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'WillBeams'))
sys.path.append(BASE_DIR)


os.environ["DJANGO_SETTINGS_MODULE"] = 'WillBeams.settings'
django.setup()


from webm.models import Webm

Webm.objects.all().delete()
