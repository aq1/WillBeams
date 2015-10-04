from django.conf.urls import include, url


urlpatterns = [
    url(r'^$', 'newapp.views.index'),
    url(r'^register/$', 'newapp.views.register'),
    url(r'^register/thankyou/$', 'newapp.views.register_after'),
]
