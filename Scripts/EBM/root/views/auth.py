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
from ..models import *
from ..services import BillCalculator, get_semester_display

@login_required(login_url='/log')
def home(request):
    """Landing page. Requires authentication."""
    return render(request, 'home.html')



def log(request):
    """
    Login view. Authenticates faculty via email + plaintext password.

    Flow: POST with email/pass → lookup faculty → compare password →
    Django authenticate() + login() → redirect to home.
    """
    if 'log' in request.POST:
        ia=faculty.objects.filter(email=request.POST.get('email'))
        if not ia:
            messages.error(request,'Account does not exist',extra_tags='log')
        else:
            ib=faculty.objects.get(email=request.POST.get('email'))
            if ib.password==request.POST.get('pass'):
                login(request,authenticate(username=ib.username,email=ib.email,password=ib.password))
                return redirect(reverse('home'))
            else:
                messages.error(request,'Passwords do not match',extra_tags='log')
    return render(request, 'log.html')



def logOut(request):
    """Log out the current user and redirect to login page."""
    logout(request)
    return redirect(reverse('log'))



