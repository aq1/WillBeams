from django.core.management.base import BaseCommand, CommandError
from addvideo import add_prepared_video
# import argparse

# add_prepared_video(video_filename, video_length, preview_filename=None, nsfw_source=False, tags=None)


class Command(BaseCommand):
    help = 'Add video by hand for testing website'

    def add_arguments(self, parser):
        parser.add_argument('webm', help='Webm file')
        parser.add_argument('length', type=int, help='Length of video in seconds')
        parser.add_argument('--preview', help='Preview image file')
        parser.add_argument('--nsfw', action='store_true', help='Mark video as NSFW')
        parser.add_argument('--tag', nargs='*', help='Tags for added video')

    def handle(self, *args, **options):
        add_prepared_video(
            options['webm'], options['length'],
            preview_filename=options['preview'],
            nsfw_source=options['nsfw'],
            tags=options['tag']
        )
