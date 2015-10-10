#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess

import tempfile

import json

import time

from math import floor

FFMPEG_BIN = 'ffmpeg' if not platform.system() == 'Window' else 'ffmpeg.exe'
FFPROBE_BIN = 'ffprobe' if not platform.system() == 'Window' else 'ffprobe.exe'
DEFAULT_FF_PATH = './ffmpeg/' if os.path.isdir('./ffmpeg') and os.path.exists('./ffmpeg/'+FFMPEG_BIN) else ""

DEFAULT_FFMPEG_BIN = os.path.join(DEFAULT_FF_PATH, FFMPEG_BIN)
DEFAULT_FFPROBE_BIN = os.path.join(DEFAULT_FF_PATH, FFPROBE_BIN)

REQUIRED_FFPROBE_OPTIONS = ['-hide_banner', '-v', 'quiet', '-print_format', 'json=c=1']
DEFAULT_FFPROBE_OPTIONS = ['-show_format', '-show_streams']

DEFAULT_FFMPEG_OPTIONS = ['-hide_banner', '-v', 'quiet', '-an']

# ~THUMBS_DIR = '/tmp/'
THUMBS_DIR = tempfile.TemporaryDirectory().name

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

        videostreams = [x for x in file_info['streams'] if x['codec_type']=='video']
        audiostreams = [x for x in file_info['streams'] if x['codec_type']=='audio']

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


def get_file_info(filename, options=DEFAULT_FFPROBE_OPTIONS):

    ff_options = [DEFAULT_FFPROBE_BIN, '-i', filename] + REQUIRED_FFPROBE_OPTIONS + options

    file_info = json.loads(subprocess.check_output(ff_options).decode('utf-8'))

    return file_info


def generate_thumbs(filename,
                    minstep=1,
                    count=1,
                    thumbs_dir=os.path.abspath(THUMBS_DIR),
                    width=-1,
                    height=-1,
                    cwidth=0,
                    cheight=0):

    ffinfo = FFInfo(filename, get_file_info(filename, DEFAULT_FFPROBE_OPTIONS))

    cur_file = os.path.join(thumbs_dir, ffinfo.filename[:-5])

    duration = float(ffinfo.duration)

    time_params = rate_dur(duration, count, minstep)

    print('>>>RATE_DUR:', time_params)

    ss = time_params['-ss']
    t = time_params['-t']
    r = time_params['-r']

    # ~step = duration/(count)
    # ~ss = step//2 if count%2 else step

    # ~fps_f = 'fps='+str(fps)
    # ~select_f = 'select=gt(scene\,0.1)'
    scale_f = 'scale='+str(width)+':'+str(height)
    crop_f = "crop=w='min(iw,"+str(cwidth)+")':h='min(ih,"+str(cheight if cheight else cwidth)+")'"

    vfilters = scale_f+', '+crop_f

    thumb_postfix = """_thumb_%02d.jpg"""

    args = [DEFAULT_FFMPEG_BIN,
            '-i', filename,
            '-ss', str(ss),
            '-vf', str(vfilters),
            '-r', str(r),
            '-t', str(t),
            '-f', 'image2'] \
            + DEFAULT_FFMPEG_OPTIONS \
            + [cur_file+thumb_postfix]

    subprocess.check_call(args)

    thumbs_list = [os.path.join(thumbs_dir, f) for f in os.listdir(thumbs_dir)]

    return thumbs_list


def webm_info(filename):

    return FFInfo(get_file_info(filename))


class Webminfo(FFInfo):

    def __init__(self, filename, minstep, count, **kwargs):

        file_info = get_file_info(filename)
        FFInfo.__init__(self, filename, file_info)

        self.thumbs_tmp_dir = tempfile.TemporaryDirectory()

        self.thumbs = generate_thumbs(filename,
                                        minstep,
                                        count,
                                        thumbs_dir=self.thumbs_tmp_dir.name,
                                        **kwargs
                                        )

    def __enter__(self):

        return self

    def __exit__(self, typeof, value, traceback):

        self.thumbs_tmp_dir.cleanup()
        pass


def rate_dur(duration, count=1, cminstep=5):
    gap_length = duration / count
    gap_length = max(cminstep, gap_length)
    gap_length = min(duration, gap_length)
    gap_count = floor(duration / gap_length)
    center = duration / 2
    offset = center - gap_count * gap_length / 2
    offset += gap_length / 2
    dur = gap_count * gap_length
    dur = min(dur, duration - offset)

    gap_length = dur/gap_count
    
    return {
        '-ss': offset,
        '-t': dur,
        '-r': 1 / gap_length
    }


if __name__ == '__main__':

    # ~path = "/media/DATA/Downloads/Видео/103151009" if not platform.system() == 'Window' else "C:\\Users\\Andrew\\Downloads\\Видео\\103151009"
    path = sys.argv[1]

    webms = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.lower().endswith('.webm')][0:1]
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    print(">>>LOADING FILES INFO")

    last_time = time.process_time()

    for webm in webms:
        get_file_info(webm)

    current_time = time.process_time()

    delta_time = current_time - last_time
    print("TOTALLY (time): %d ms, %d webms" %(delta_time*1000, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time*1000/len(webms))

    print(">>>THUMBS GEN\n")

    last_time = time.process_time()

    for ww in enumerate(webms):
        webm = ww[1]
        print('>>>WEBM', webm)
        with Webminfo(webm, minstep=1, count=5, width=600, cwidth=400) as w:
            print()
            print(w.filename)
            print(w.path)
            print(w.duration, w.width, w.height)
            for i in w.thumbs:
                print(i)

    current_time = time.process_time()

    delta_time = current_time - last_time
    print("TOTALLY (time): %d ms, %d webms" %(delta_time*1000, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time*1000/len(webms))
