from django.contrib import admin
from django.core.urlresolvers import reverse

from webm.models import Webm, Tag, WebmUrl


class WebmUrlInline(admin.StackedInline):
    model = WebmUrl
    extra = 0


@admin.register(Webm)
class WebmAdmin(admin.ModelAdmin):
    readonly_fields = ['md5', 'added']
    list_display = [
        'thumb_img', 'rating', 'md5', 'is_safe_for_work', 'added']
    ordering = ['-rating']

    inlines = [WebmUrlInline]
    search_fields = ['md5', 'thumbnail']

    def is_safe_for_work(self, obj):
        return not obj.nsfw

    is_safe_for_work.boolean = True
    is_safe_for_work.short_description = 'Safe for work?'

    def thumb_img(self, obj):
        html = '<img style="max-width:100%%; \
                max-height:100%%; width:200px;" \
                src="%s" alt="No thumb">'
        try:
            return html % obj.thumb.url
        except ValueError:
            return html % ''

    thumb_img.allow_tags = True


@admin.register(WebmUrl)
class WebmUrlAdmin(admin.ModelAdmin):
    list_display = ['webm', 'url', 'webm_model']
    ordering = ['webm__rating']
    search_fields = ['webm__thumbnail', 'webm__md5']

    def webm_model(self, obj):
        webm = reverse('admin:webm_webm_change', args=[obj.webm.pk])
        return '<a href="{}">Webm</a>'.format(webm)

    webm_model.allow_tags = True


admin.site.register(Tag)
