from django.conf.urls import url
from .views.rental_create_view import RentalCreateView
from .views.rental_detail_view import RentalDetailView
from .views.rental_state_view import RentalStateView

app_name = 'rental'
urlpatterns = [
    url(r'^create/$', RentalCreateView.as_view(), name='create'),
    url(r'^(?P<rental_uuid>[0-9a-z\-]+)/$', RentalDetailView.as_view(), name='detail'),
    url(r'^(?P<rental_uuid>[0-9a-z\-]+)/state/$', RentalStateView.as_view(), name='state'),
]
