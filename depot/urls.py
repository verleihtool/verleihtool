from django.conf.urls import url
from .views.depot_create_rental_view import DepotCreateRentalView
from .views.depot_detail_view import DepotDetailView
from .views.depot_index_view import DepotIndexView
from .views.depot_rentals_view import DepotRentalsView

app_name = 'depot'
urlpatterns = [
    url(r'^$', DepotIndexView.as_view(), name='index'),
    url(r'^(?P<depot_id>[0-9]+)/$', DepotDetailView.as_view(), name='detail'),
    url(r'^(?P<depot_id>[0-9]+)/rentals/$', DepotRentalsView.as_view(), name='rentals'),
    url(r'^(?P<depot_id>[0-9]+)/rentals/create/$', DepotCreateRentalView.as_view(),
        name='create_rental')
]
