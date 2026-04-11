"""
Root URL configuration — includes all URL modules.

This is the ROOT_URLCONF (set in settings.py as 'root.urls').
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('root.urls.auth')),
    path('', include('root.urls.committee')),
    path('', include('root.urls.course')),
    path('', include('root.urls.billing')),
]
