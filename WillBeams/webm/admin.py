from django.contrib import admin

from webm.models import Webm, Tag, WebmTag, WebmUrl


@admin.register(Webm)
class WebmAdmin(admin.ModelAdmin):
    fields = ['video', 'thumbnail', 'rating', 'nsfw']
    readonly = ['md5', 'added']
    list_display = [
        'thumbnail_img', 'rating', 'md5', 'is_safe_for_work', 'added']
    ordering = ['-rating']


@admin.register(WebmUrl)
class WebmUrlAdmin(admin.ModelAdmin):
    list_display = ['webm', 'url']


admin.site.register(Tag)
admin.site.register(WebmTag)
