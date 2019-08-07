from django.urls import path
from .views.depot_create_rental_view import DepotCreateRentalView
from .views.depot_detail_view import DepotDetailView
from .views.depot_index_view import DepotIndexView
from .views.depot_rentals_view import DepotRentalsView

app_name = 'depot'
urlpatterns = [
    path('', DepotIndexView.as_view(), name='index'),
    path('<int:depot_id>/', DepotDetailView.as_view(), name='detail'),
    path('<int:depot_id>/rentals/', DepotRentalsView.as_view(), name='rentals'),
    path('<int:depot_id>/rentals/create/', DepotCreateRentalView.as_view(),
         name='create_rental')
]
