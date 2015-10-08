from django.contrib import admin
from django.core.urlresolvers import reverse

from newapp.models import Webm, Tag, View

class TagInlineAdmin(admin.TabularInline):
    model = Webm.tag.through

@admin.register(Webm)
class WebmAdmin(admin.ModelAdmin):
    readonly_fields = ['added']
    list_display = ['thumb_img', 'added', 'likes_count', 'views_count', 'tag_list']
    list_filter = ['tag__name',]
    #fields = ['video', 'thumb', 'length', 'added', 'nsfw_source', 'blacklisted']
    inlines = (TagInlineAdmin,)

    def likes_count(self, obj):
        return obj.likes.count()

    def views_count(self, obj):
        return View.objects.filter(webm=obj).count()

    def tag_list(self, obj):
        return ','.join(obj.tag.values_list('name', flat=True))

    def thumb_img(self, obj):
        html = '<img style="max-width:100%%; \
                max-height:100%%; width:200px;" \
                src="%s" alt="No thumb">'
        try:
            return html % obj.thumb.url
        except ValueError:
            return html % ''
    ordering = ['-added']

    thumb_img.allow_tags = True



admin.site.register(Tag)
