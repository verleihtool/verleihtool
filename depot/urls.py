from django.conf.urls import url
from . import views

app_name = 'depot'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<depot_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<depot_id>[0-9]+)/rentals/$', views.rentals, name='rentals'),
    url(r'^(?P<depot_id>[0-9]+)/rentals/create/$', views.create_rental, name='create_rental')
]
