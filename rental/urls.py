from django.urls import path
from .views.rental_create_view import RentalCreateView
from .views.rental_detail_view import RentalDetailView
from .views.rental_state_view import RentalStateView

app_name = 'rental'
urlpatterns = [
    path('create/', RentalCreateView.as_view(), name='create'),
    path('<uuid:rental_uuid>/', RentalDetailView.as_view(), name='detail'),
    path('<uuid:rental_uuid>/state/', RentalStateView.as_view(), name='state'),
]
