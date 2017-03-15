from django.conf.urls import url
from . import views

app_name = 'depot'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<depot_id>[0-9]+)/$', views.detail, name='detail'),
]