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



