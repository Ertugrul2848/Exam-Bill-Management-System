"""Authentication URL patterns."""

from django.urls import path
from ..views import home, log, logOut

urlpatterns = [
    path('', home, name='home'),
    path('accounts/login/', log, name="log"),
    path('log/', log, name="log"),
    path('logOut/', logOut, name="logOut"),
]
