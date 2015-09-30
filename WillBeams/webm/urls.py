from django.conf.urls import url
from rest_framework import routers

from .views import index

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'webm', views.WebmViewSet)

urlpatterns = [
    #url(r'', index),
    url(r'', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

