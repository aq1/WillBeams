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

REQUIRED_FFPROBE_OPTIONS = ['-hide_banner', '-print_format', 'json=c=1']  # , '-v', 'quiet']
DEFAULT_FFPROBE_OPTIONS = ['-show_format', '-show_streams']

DEFAULT_FFMPEG_OPTIONS = ['-pix_fmt', 'yuvj420p', '-hide_banner', '-an']  # , '-v', 'quiet']

THUMBS_DIR = tempfile.TemporaryDirectory()
THUMBS_DIR_NAME = THUMBS_DIR.name

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

        videostreams = [x for x in file_info['streams'] if x['codec_type'] == 'video']
        audiostreams = [x for x in file_info['streams'] if x['codec_type'] == 'audio']

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


def get_file_info(filename, options=DEFAULT_FFPROBE_OPTIONS):

    ff_options = \
        [DEFAULT_FFPROBE_BIN, '-i', filename] \
        + REQUIRED_FFPROBE_OPTIONS \
        + options

    file_info = json.loads(subprocess.check_output(ff_options).decode('utf-8'))

    return file_info


def generate_thumbs(
        filename,
        minstep=1,
        count=1,
        vfilters="",
        thumbs_dir=os.path.abspath(THUMBS_DIR_NAME)
):

    ffinfo = FFInfo(filename, get_file_info(filename, DEFAULT_FFPROBE_OPTIONS))

    cur_file = os.path.join(thumbs_dir, ffinfo.filename[:-5])

    duration = float(ffinfo.duration)

    time_params = rate_dur(duration, count, minstep)

    ss = time_params['-ss']
    t = time_params['-t']
    r = time_params['-r']

    # ~fps_f = 'fps='+str(fps)
    # ~select_f = 'select=gt(scene\,0.1)'

    thumb_postfix = '_thumb_%02d.jpg'

    args = [
        DEFAULT_FFMPEG_BIN,
        '-i', filename,
        '-ss', str(ss),
        '-vf' if vfilters else '', str(vfilters),
        '-r', str(r),
        '-t', str(t),
        '-f', 'image2'
    ] \
        + DEFAULT_FFMPEG_OPTIONS \
        + [cur_file+thumb_postfix]

    subprocess.check_call(args)

    thumbs_list = [os.path.join(thumbs_dir, f) for f in os.listdir(thumbs_dir)]

    return thumbs_list


def webm_info(filename):

    return FFInfo(get_file_info(filename))


class WebmInfo(FFInfo):

    def __init__(self, filename):

        file_info = get_file_info(filename)
        FFInfo.__init__(self, filename, file_info)


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

    path = sys.argv[1]

    webms = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.lower().endswith('.webm')]
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    print(">>>LOADING FILES INFO")

    last_time = time.process_time()

    for webm in webms:
        get_file_info(webm)

    current_time = time.process_time()

    delta_time = current_time - last_time

    print("TOTALLY (time): %d ms, %d webms" % (delta_time*1000, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time*1000/len(webms))

    print("\n\n\n")

    print(">>>THUMBS GEN\n")

    last_time = time.process_time()

    width = height = 600
    cwidth = cheight = 400

    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_name = temp_dir.name

    for webm in webms:
        print(">>>WEBM", webm)

        w = WebmInfo(webm)

        print(w.filename)
        print(w.path)
        print(w.duration, w.width, w.height)

        scale_f = 'scale='+str(width)+':'+str(height)
        crop_f = "crop=w='min(iw,"+str(cwidth)+")':h='min(ih,"+str(cheight if cheight else cwidth)+")'"

        vfilters = scale_f+', '+crop_f

        thumbs = generate_thumbs(
            webm,
            minstep=1,
            count=5,
            vfilters=vfilters,
            thumbs_dir=temp_dir_name
        )

        for i in thumbs:
            print(i)
        print()

    current_time = time.process_time()

    delta_time = current_time - last_time

    print("\n\n\n")
    print("TOTALLY (time): %d ms, %d webms" % (delta_time*1000, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time*1000/len(webms))
