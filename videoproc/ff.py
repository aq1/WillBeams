#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess

import json

from distutils.spawn import find_executable

import time
# ~import sfml as sf
from sys import getsizeof as size

DEFAULT_FFMPEG_BIN = 'ffmpeg' if not platform.system() == 'Window' else 'ffmpeg.exe'
DEFAULT_FFPROBE_BIN = 'ffprobe' if not platform.system() == 'Window' else 'ffprobe.exe'
DEFAULT_FF_PATH = './ffmpeg/' if os.path.isdir('./ffmpeg') and os.path.exists('./ffmpeg/'+DEFAULT_FFMPEG_BIN) else ""

REQUIRED_FFPROBE_OPTIONS = ['-hide_banner', '-v', 'quiet', '-print_format', 'json=c=1']
DEFAULT_FFPROBE_OPTIONS = ['-show_format', '-show_streams']

DEFAULT_FFMPEG_OPTIONS = ['-hide_banner', '-v', 'quiet', '-an']

THUMBS_DIR = '/tmp/ram/'

EMPTY_VIDEO = {
                'height': 0,
                'width': 0,
                'duration': 0,
                'codec_name': None
                }

EMPTY_AUDIO = {
                'codec_name': None
                }


class FFInfo(object):

    def __init__(self, path, file_info):

        self.path = path

        file_format = file_info['format']

        videostreams = [ x for x in file_info['streams'] if x['codec_type']=='video' ]
        audiostreams = [ x for x in file_info['streams'] if x['codec_type']=='audio' ]

        videostream = videostreams[0] if videostreams else EMPTY_VIDEO
        audiostream = audiostreams[0] if audiostreams else EMPTY_AUDIO

        self.videostream = videostream
        self.audiostream = audiostream

        self.videocodec = videostream['codec_name']
        self.audiocodec = audiostream['codec_name']

        self.height = int(videostream['height'])
        self.width = int(videostream['width'])
        self.duration = float(file_format['duration'])
        self.filename = os.path.basename(file_format['filename'])

        self.thumbs = []

    def __enter__(self):

        return self

    def __exit__(self, typeof, value, traceback):

        pass

class FF(object):

    def __init__(self, ffstorage=None):

        if DEFAULT_FF_PATH:
            self._ff_path = os.path.abspath(DEFAULT_FF_PATH)
            self._ffmpeg = os.path.abspath(os.path.join(DEFAULT_FF_PATH, DEFAULT_FFMPEG_BIN))
            self._ffprobe = os.path.abspath(os.path.join(DEFAULT_FF_PATH, DEFAULT_FFPROBE_BIN))

        else:
            self._ff_path = os.path.abspath(find_executable(DEFAULT_FFMPEG_BIN))
            self._ffmpeg = self._ff_path
            self._ffprobe = self._ff_path

        try:
            assert(not self._ff_path == '')
        except:
            raise("FFMPEG NOT FOUND")

        self._ffstorage = ffstorage

        if not ffstorage is None:
            self._store = lambda filename, file_info: ffstorage.store(filename, file_info)
        else:
            self._store = lambda x, y: None

    def get_file_info(self, filename, options=DEFAULT_FFPROBE_OPTIONS):

        if not self._ffstorage is None and filename in self._ffstorage._storage:
            ffinfo = self._ffstorage.get(filename)
            return ffinfo

        ff_options = [DEFAULT_FFPROBE_BIN, '-i', filename] + REQUIRED_FFPROBE_OPTIONS + options

        try:
            file_info = json.loads(subprocess.check_output(ff_options).decode('utf-8'))
        except:
            pass
        ffinfo = FFInfo(filename, file_info)

        return ffinfo

    def load_file_info(self, filename, options=DEFAULT_FFPROBE_OPTIONS):

        ffinfo = self.get_file_info(filename, options)

        if not self._ffstorage is None:
            self._store(filename, ffinfo)

        return ffinfo

    def generate_thumbs(self, filename, minstep=1, count=1, thumbs_dir=os.path.abspath(THUMBS_DIR), width=-1, height=-1, cwidth=0, cheight=0):

        ffinfo = self.get_file_info(filename, DEFAULT_FFPROBE_OPTIONS)

        duration = float(ffinfo.duration)

        cur_file = os.path.join(thumbs_dir, ffinfo.filename[:-5])

        # ~step = max(minstep, duration/(count))
        step = duration/(count)

        fps = '1/'+str(step)

        # ~ss = step
        ss = step if count%2 else step//2
         
        fps_f = 'fps='+str(fps)
        scale_f = 'scale='+str(width)+':'+str(height)
        crop_f = "crop=w='min(iw,"+str(cwidth)+")':h='min(ih,"+str(cheight if cheight else cwidth)+")'"
        
        select_f = 'select=gt(scene\,0.1)'

        # ~vfilters = fps_f+', '+scale_f
        vfilters = scale_f+', '+crop_f

        thumb_postfix = """_thumb_%02d.jpg"""

        args = [DEFAULT_FFMPEG_BIN,
                '-i', filename,
                '-ss', str(ss),
                '-vf', str(vfilters),
                '-r', str(1/(step+1)),
                # ~'-vsync', 'vfr',
                # ~'-vframes', str(count+3),
                '-f', 'image2'] \
                + DEFAULT_FFMPEG_OPTIONS \
                + [cur_file+thumb_postfix]

        try:
            subprocess.check_call(args)
            ffstorage = self.get_file_info(filename)
            ffstorage.thumbs.extend([cur_file+thumb_postfix %(i,) for i in range(1, count+1)])
        except:
            print("ERROR CREATING THUMB")


    def webm_info(self, filename, minstep, count, **kwargs):

        ffinfo = self.load_file_info(filename)

        if ffinfo.thumbs == []:
            self.generate_thumbs(filename, minstep=minstep, count=count)

        return ffinfo


class FFStorage(object):

    def __init__(self):

        self._storage = {}

    def store(self, filename, ffinfo):

        self._storage[filename] = ffinfo

    def get(self, filename):

        return self._storage.get(filename)

    def set(self, filename, **kwargs):

        ffinfo = self._storage.get(filename)

        if not ffinfo is None:
            ffinfo.__dict__.update(kwargs)

if __name__ == '__main__':

    ffstorage = FFStorage()
    ff = FF(ffstorage)

    path = "/media/DATA/Downloads/Видео/103151009" if not platform.system() == 'Window' else "C:\\Users\\Andrew\\Downloads\\Видео\\103151009"

    webms = [ os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.lower().endswith('.webm') ][0:3]
    files = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) ]

    print(">>>LOADING FILES INFO")

    # ~clock = sf.Clock()
    # ~last_time = 0
    # ~clast_time = clock.elapsed_time.milliseconds
    last_time = time.process_time()

    for webm in webms:
        ff.load_file_info(webm)

    # ~ccurrent_time = clock.elapsed_time.milliseconds
    current_time = time.process_time()

    delta_time = current_time - last_time
    # ~cdelta_time = ccurrent_time - clast_time
    print("TOTALLY (time): %d ms, %d webms" %(delta_time*1000, len(webms)))
    # ~print("TOTALLY (sfml): %d ms, %d webms" %(cdelta_time, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time*1000/len(webms))
    # ~print("<MILLISECONDS> (sfml) PER WEBM:", cdelta_time/len(webms))


    print(">>>THUMBS GEN")

    # ~clock = sf.Clock()
    # ~last_time = 0
    # ~clast_time = clock.elapsed_time.milliseconds
    last_time = time.process_time()

    for ww in enumerate(webms):
        webm = ww[1]
        ff.generate_thumbs(webm, count=5, width=600, cwidth=400)

        with ff.webm_info(webm, minstep=10, count=5) as w:
            print()
            print(w.filename)
            print(w.path)
            print(w.duration, w.width, w.height)
            for i in w.thumbs:
              print(i)

    # ~ccurrent_time = clock.elapsed_time.milliseconds
    current_time = time.process_time()

    delta_time = current_time - last_time
    # ~cdelta_time = ccurrent_time - clast_time
    print("TOTALLY (time): %d ms, %d webms" %(delta_time*1000, len(webms)))
    # ~print("TOTALLY (sfml): %d ms, %d webms" %(cdelta_time, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time*1000/len(webms))
    # ~print("<MILLISECONDS> (sfml) PER WEBM:", cdelta_time/len(webms))
