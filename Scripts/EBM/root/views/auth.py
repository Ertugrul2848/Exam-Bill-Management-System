"""Authentication views."""

from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from xhtml2pdf import pisa
from ..models import faculty, Session, Semester
from ..services import BillCalculator, get_semester_display

@login_required(login_url='/log')
def home(request):
    """Landing page. Requires authentication. Redirects incomplete profiles."""
    try:
        teacher = faculty.objects.get(username=request.user.username)
        if not teacher.is_profile_complete:
            return redirect(reverse('complete_profile'))
    except faculty.DoesNotExist:
        pass
    return render(request, 'home.html')



def log(request):
    """
    Login view. Authenticates faculty via email + password using Django auth.

    Flow: POST with email/pass → lookup faculty by email →
    Django authenticate() with username+password → login() → redirect to home.
    """
    if 'log' in request.POST:
        email = request.POST.get('email', '').strip()
        password = request.POST.get('pass', '')
        try:
            fac = faculty.objects.get(email=email)
        except faculty.DoesNotExist:
            messages.error(request, 'Account does not exist', extra_tags='log')
            return render(request, 'log.html')

        user = authenticate(request, username=fac.username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('home'))
        else:
            messages.error(request, 'Passwords do not match', extra_tags='log')
    return render(request, 'log.html')



def logOut(request):
    """Log out the current user and redirect to login page."""
    logout(request)
    return redirect(reverse('log'))



TITLE_CHOICES = [
    ('Professor', 'Professor'),
    ('Associate Professor', 'Associate Professor'),
    ('Assistant Professor', 'Assistant Professor'),
    ('Lecturer', 'Lecturer'),
]

@login_required(login_url='/log')
def profile(request):
    """View and update the current user's faculty profile."""
    fac = get_object_or_404(faculty, email=request.user.email)
    if request.method == 'POST':
        fac.name = request.POST.get('name', fac.name)
        fac.title = request.POST.get('title', fac.title)
        fac.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect(reverse('profile'))
    return render(request, 'auth/profile.html', {'fac': fac, 'title_choices': TITLE_CHOICES})



@login_required(login_url='/log')
def change_password(request):
    """Change the current user's password with current password verification."""
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new_pass = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect!')
            return render(request, 'auth/change_password.html')
        if new_pass != confirm:
            messages.error(request, 'New passwords do not match!')
            return render(request, 'auth/change_password.html')
        if len(new_pass) < 8:
            messages.error(request, 'Password must be at least 8 characters!')
            return render(request, 'auth/change_password.html')

        request.user.set_password(new_pass)
        request.user.save()
        # Update faculty password too
        try:
            fac = faculty.objects.get(email=request.user.email)
            fac.password = new_pass
            fac.save()
        except:
            pass
        # Keep user logged in after password change
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Password changed successfully!')
        return redirect(reverse('profile'))
    return render(request, 'auth/change_password.html')



def forgot_password(request):
    """Send a password-reset link to the user's registered email address."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            fac = faculty.objects.get(email=email)
            user = User.objects.get(username=fac.username)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{request.scheme}://{request.get_host()}{reverse('reset_password', args=[uid, token])}"
            send_mail(
                'EBM — Password Reset Request',
                f'Hello {fac.name or fac.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you did not request a password reset, please ignore this email.',
                'noreply@ebm.edu',
                [email],
            )
            messages.success(request, 'Password reset link sent to your email.')
        except (faculty.DoesNotExist, User.DoesNotExist):
            messages.error(request, 'No account found with that email address.')
    return render(request, 'auth/forgot_password.html')



def reset_password(request, uidb64, token):
    """Validate the reset token and allow the user to set a new password."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'This password reset link is invalid or has expired.')
        return render(request, 'auth/reset_password.html', {'valid_link': False})

    if request.method == 'POST':
        new_pass = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')
        if len(new_pass) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif new_pass != confirm:
            messages.error(request, 'Passwords do not match.')
        else:
            user.set_password(new_pass)
            user.save()
            # Keep faculty model in sync
            try:
                fac = faculty.objects.get(username=user.username)
                fac.password = new_pass
                fac.save()
            except faculty.DoesNotExist:
                pass
            messages.success(request, 'Password reset successfully. You can now log in.')
            return redirect(reverse('log'))
    return render(request, 'auth/reset_password.html', {'valid_link': True})
