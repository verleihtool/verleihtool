from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


app_name = 'login'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
