from django.conf.urls import include, url


urlpatterns = [
    url(r'^$', 'newapp.views.index'),
]
