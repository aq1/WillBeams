from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'newapp.views.index'),
    url(r'^register/$', 'newapp.views.register'),
    url(r'^register/thankyou/$', 'newapp.views.register_after'),

    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'newapp.views.logout', name='logout'),
    url(
        r'^password_change/$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'registration/password_change.html'},
        name='password_change'
    ),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
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
