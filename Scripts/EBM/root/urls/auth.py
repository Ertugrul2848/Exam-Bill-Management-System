"""Authentication URL patterns."""

from django.urls import path
from ..views import (
    home, log, logOut, profile, change_password, forgot_password, reset_password,
    register, pending_registrations, approve_registration, reject_registration, add_teacher_direct, complete_profile,
    register_with_token, resend_invitation, cancel_invitation,
    manage_moderators, edit_moderator, remove_moderator,
    transfer_chairman,
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
    path('resend-invitation/<int:pk>/', resend_invitation, name='resend_invitation'),
    path('cancel-invitation/<int:pk>/', cancel_invitation, name='cancel_invitation'),
    path('complete-profile/', complete_profile, name='complete_profile'),
    path('register/<uuid:token>/', register_with_token, name='register_with_token'),
    path('moderators/', manage_moderators, name='manage_moderators'),
    path('moderators/<int:pk>/edit/', edit_moderator, name='edit_moderator'),
    path('moderators/<int:pk>/remove/', remove_moderator, name='remove_moderator'),
    path('profile/', profile, name='profile'),
    path('change-password/', change_password, name='change_password'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),
    path('transfer-chairman/', transfer_chairman, name='transfer_chairman'),
]
