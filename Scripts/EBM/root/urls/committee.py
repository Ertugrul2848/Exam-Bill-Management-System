"""Committee management URL patterns."""

from django.urls import path
from ..views import committee, createCom, viewCom, viewSem, addRole, createSem, assign_acting_chairman, remove_acting_chairman, toggle_archive, toggle_lock

urlpatterns = [
    path('committee/', committee, name="committee"),
    path('createCom/', createCom, name="createCom"),
    path('viewCom/<int:id>/', viewCom, name="viewCom"),
    path('viewSem/<int:id>/<int:id2>/', viewSem, name="viewSem"),
    path('addRole/<int:id>/<int:id2>/', addRole, name="addRole"),
    path('createSem/<int:id>/', createSem, name="createSem"),
    path('assign-acting/<int:id>/<int:id2>/', assign_acting_chairman, name='assign_acting'),
    path('remove-acting/<int:id>/<int:id2>/', remove_acting_chairman, name='remove_acting'),
    path('toggle-archive/<int:id>/<int:id2>/', toggle_archive, name='toggle_archive'),
    path('toggle-lock/<int:id>/<int:id2>/', toggle_lock, name='toggle_lock'),
]
