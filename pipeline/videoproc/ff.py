#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import tempfile
import json
import time
from math import floor


FFMPEG_BIN = os.environ.get('FFMPEG') or ('ffmpeg' if not platform.system() == 'Window' else 'ffmpeg.exe')
FFPROBE_BIN = os.environ.get('FFPROBE') or ('ffprobe' if not platform.system() == 'Window' else 'ffprobe.exe')

REQUIRED_FFPROBE_OPTIONS = ['-hide_banner', '-print_format', 'json=c=1']
DEFAULT_FFPROBE_OPTIONS = ['-show_format', '-show_streams']

DEFAULT_FFMPEG_OPTIONS = ['-pix_fmt', 'yuvj420p', '-hide_banner', '-an']

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
    'dummy object for storing ffprobe info'
    def __init__(self, path, file_info):
        self.path = path
        self.filename = os.path.basename(self.path)

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


def get_file_info(filename, options=DEFAULT_FFPROBE_OPTIONS, quiet=True):
    ff_options = [FFPROBE_BIN, '-i', filename] + REQUIRED_FFPROBE_OPTIONS + options
    if quiet:
        ff_options.extend(['-v', 'quiet'])
    return FFInfo(
        filename,
        json.loads(subprocess.check_output(ff_options).decode('utf-8'))
    )


def generate_thumbs(ffinfo, thumbs_dir, minstep=1, count=1, vfilters=None, quiet=True):
    fbase, _ = os.path.splitext(ffinfo.filename)
    fbase += '_thumb_'
    fend = '.jpg'
    fname_template = os.path.join(thumbs_dir, fbase + '%02d' + fend)
    time_params = rate_dur(ffinfo.duration, count, minstep)

    def tfile_list():
        return [f for f in os.listdir(thumbs_dir) if f.startswith(fbase) and f.endswith(fend)]

    assert not tfile_list(), 'You must clean target directory before generating thumbnails'

    # ~fps_f = 'fps='+str(fps)
    # ~select_f = 'select=gt(scene\,0.1)'

    args = [
        FFMPEG_BIN,
        '-i', ffinfo.path,
        '-ss', str(time_params['-ss']),
    ]
    if vfilters is not None:
        args.extend(['-vf', vfilters])
    args.extend([
        '-r', str(time_params['-r']),
        '-t', str(time_params['-t']),
        '-f', 'image2'
    ])
    args.extend(DEFAULT_FFMPEG_OPTIONS)
    if quiet:
        args.extend(['-v', 'quiet'])
    args.append(fname_template)

    subprocess.check_call(args)
    return list(map(lambda fname: os.path.join(thumbs_dir, fname), tfile_list()))


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
    webms = [
        os.path.join(path, f) for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.lower().endswith('.webm')
    ]
    print(">>>LOADING FILES INFO")

    last_time = time.monotonic()

    for webm in webms:
        get_file_info(webm)

    delta_time = time.monotonic() - last_time

    print('TOTALLY (time): {} ms, {} webms'.format(delta_time * 1000, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time * 1000 / len(webms))
    print("\n\n\n")

    print(">>>THUMBS GEN")

    last_time = time.monotonic()

    width = height = 600
    cwidth = cheight = 400

    for webm in webms:
        print(">>>WEBM", webm)
        with tempfile.TemporaryDirectory() as outdir:
            w = get_file_info(webm)
            print(w.filename)
            print(w.path)
            print(w.duration, w.width, w.height)

            scale_f = 'scale='+str(width)+':'+str(height)
            crop_f = "crop=w='min(iw,"+str(cwidth)+")':h='min(ih,"+str(cheight if cheight else cwidth)+")'"
            vfilters = scale_f+', '+crop_f

            thumbs = generate_thumbs(
                w,
                outdir,
                minstep=1,
                count=5,
                vfilters=vfilters
            )

            for i in thumbs:
                print(i)
        print()

    delta_time = time.monotonic() - last_time

    print("\n\n\n")
    print('TOTALLY (time): {} ms, {} webms'.format(delta_time * 1000, len(webms)))
    print("<MILLISECONDS> (time) PER WEBM:", delta_time * 1000 / len(webms))
