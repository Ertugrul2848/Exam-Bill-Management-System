"""Authentication URL patterns."""

from django.urls import path
from ..views import (
    home, log, logOut,
    register, pending_registrations, approve_registration, reject_registration, add_teacher_direct,
    manage_moderators, edit_moderator, remove_moderator,
)

urlpatterns = [
    path('', home, name='home'),
    path('accounts/login/', log, name="log"),
    path('log/', log, name="log"),
    path('logOut/', logOut, name="logOut"),
    path('register/', register, name='register'),
    path('pending-registrations/', pending_registrations, name='pending_registrations'),
    path('approve-registration/<int:pk>/', approve_registration, name='approve_registration'),
    path('reject-registration/<int:pk>/', reject_registration, name='reject_registration'),
    path('add-teacher/', add_teacher_direct, name='add_teacher_direct'),
    path('moderators/', manage_moderators, name='manage_moderators'),
    path('moderators/<int:pk>/edit/', edit_moderator, name='edit_moderator'),
    path('moderators/<int:pk>/remove/', remove_moderator, name='remove_moderator'),
]
