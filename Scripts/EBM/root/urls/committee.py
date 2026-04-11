"""Committee management URL patterns."""

from django.urls import path
from ..views import committee, createCom, viewCom, viewSem, addRole, createSem

urlpatterns = [
    path('committee/', committee, name="committee"),
    path('createCom/', createCom, name="createCom"),
    path('viewCom/<int:id>/', viewCom, name="viewCom"),
    path('viewSem/<int:id>/<int:id2>/', viewSem, name="viewSem"),
    path('addRole/<int:id>/<int:id2>/', addRole, name="addRole"),
    path('createSem/<int:id>/', createSem, name="createSem"),
]
