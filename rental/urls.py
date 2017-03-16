from django.conf.urls import url
from . import views

app_name = 'rental'
urlpatterns = [
    url(r'^create/$', views.create, name='create'),
    url(r'^(?P<rental.uuid>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<rental.uuid>[0-9]+)/update/$', views.update, name='update'),
]
