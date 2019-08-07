"""verleihtool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = i18n_patterns(
    path('', include('login.urls')),
    path('depots/', include('depot.urls')),
    path('rentals/', include('rental.urls')),
    path('admin/', admin.site.urls),
    prefix_default_language=False
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# Remove the above line in production and serve the static files properly
# https://docs.djangoproject.com/en/dev/howto/static-files/
