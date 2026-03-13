"""Main URL configuration."""
from django.contrib import admin
from django.urls import path, re_path, include

from .views import serve_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('reports/', include('reports.urls')),
    path('shelters/', include('shelters.urls')),
    # Serve media in production (Django's static() returns 404 when DEBUG=False)
    re_path(r'^media/(?P<path>.*)$', serve_media),
]
