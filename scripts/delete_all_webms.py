confirm = input('Really? Y/N')

if confirm not in ('y', 'Y', 'yes', 'yeap', 'da', 'aga', 'konechno, go'):
    exit()

import os
import sys

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "WillBeams.settings"
sys.path.append("WillBeams/")

django.setup()

from will_beams.models import Webm

Webm.objects.all().delete()
