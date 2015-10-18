from django.conf.urls import url
from .hashtag import hashtag_regex_string


urlpatterns = [
    url(r'^register/$', 'newapp.views.register'),
    url(r'^register/thankyou/$', 'newapp.views.register_after'),

    url(
        r'^login/$',
        'django.contrib.auth.views.login',
        {'extra_context': {'active': 'login'}},
        name='login'
    ),
    url(r'^logout/$', 'newapp.views.logout', name='logout'),
    url(
        r'^password_change/$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'registration/password_change.html'},
        name='password_change'
    ),
    url(
        r'^password_change/done/$',
        'django.contrib.auth.views.password_change_done',
        {'template_name': 'registration/password_change_done.html'},
        name='password_change_done'
    ),
]


# Append to urlpatterns to enable email logic
[
    url(
        r'^password_reset/$',
        'django.contrib.auth.views.password_reset',
        {'template_name': 'registration/password_reset.html'},
        name='password_reset'
    ),
    url(
        r'^password_reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'registration/password_reset_done.html'},
        name='password_reset_done'
    ),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(
        r'^reset/done/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'registration/password_reset_complete.html'},
        name='password_reset_complete'
    ),
]

# Video lists

urlpatterns += [
    url(r'^$', 'newapp.views.new_videos', name='home'),
    url(r'^liked/$', 'newapp.views.liked_videos'),
    url(r'^favourite/$', 'newapp.views.favourite_videos'),
    url(r'^tag/(?P<tag>{})/$'.format(hashtag_regex_string), 'newapp.views.tag_videos'),
    url(r'^usertag/(?P<tag>{})/$'.format(hashtag_regex_string), 'newapp.views.usertag_videos'),
    url(r'^video/(?P<vid>[1-9][0-9]*)/$', 'newapp.views.video'),
    url(r'^video/like/$', 'newapp.views.toggle_like'),
    url(r'^video/favourite/$', 'newapp.views.toggle_favourite'),
    url(r'^video/nsfw/$', 'newapp.views.toggle_nsfw'),
    url(r'^video/tags/$', 'newapp.views.update_tags'),
    url(r'^video/delete/$', 'newapp.views.video_delete'),
]
