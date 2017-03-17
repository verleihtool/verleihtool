from django.conf.urls import url
from . import views

app_name = 'rental'
urlpatterns = [
    url(r'^create/$', views.create, name='create'),
    url(r'^(?P<rental_uuid>[0-9a-z\-]+)/$', views.detail, name='detail'),
    url(r'^(?P<rental_uuid>[0-9a-z\-]+)/update/$', views.update, name='update'),
]
