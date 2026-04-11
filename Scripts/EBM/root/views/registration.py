"""Teacher registration and chairman approval views."""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..models import faculty, RegistrationRequest


def register(request):
    """Public registration form for new teachers."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        title = request.POST.get('title', '').strip()
        password = request.POST.get('password', '').strip()

        if not all([name, email, title, password]):
            messages.error(request, 'All fields are required!')
            return render(request, 'auth/register.html')

        if RegistrationRequest.objects.filter(email=email).exists():
            messages.error(request, 'A registration request with this email already exists!')
            return render(request, 'auth/register.html')

        if faculty.objects.filter(email=email).exists():
            messages.error(request, 'A teacher with this email already exists!')
            return render(request, 'auth/register.html')

        RegistrationRequest.objects.create(
            name=name, email=email, title=title, password=password
        )
        messages.success(request, 'Your application has been submitted. Please wait for chairman approval.')
        return redirect(reverse('log'))

    return render(request, 'auth/register.html')


@login_required(login_url='/log')
def pending_registrations(request):
    """Chairman-only: list pending registration requests."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    pending = RegistrationRequest.objects.filter(status='pending')
    return render(request, 'auth/pending_registrations.html', {'pending': pending})


@login_required(login_url='/log')
def approve_registration(request, pk):
    """Chairman-only: approve a registration request."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    reg = get_object_or_404(RegistrationRequest, pk=pk, status='pending')

    # Create username from email (before @)
    username = reg.email.split('@')[0]
    # Ensure unique username
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    # Create Django User
    user = User.objects.create_user(
        username=username, email=reg.email, password=reg.password
    )

    # Create faculty record
    faculty.objects.create(
        username=username, email=reg.email,
        name=reg.name, title=reg.title, password=reg.password
    )

    reg.status = 'approved'
    reg.save()

    messages.success(request, f'{reg.name} has been approved as a teacher.')
    return redirect(reverse('pending_registrations'))


@login_required(login_url='/log')
def reject_registration(request, pk):
    """Chairman-only: reject a registration request."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    reg = get_object_or_404(RegistrationRequest, pk=pk, status='pending')
    reg.status = 'rejected'
    reg.save()

    messages.success(request, f'{reg.name} has been rejected.')
    return redirect(reverse('pending_registrations'))
