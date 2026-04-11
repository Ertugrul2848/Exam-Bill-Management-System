"""Teacher registration and chairman approval views."""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address!')
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
def add_teacher_direct(request):
    """Chairman-only: add teacher directly — email only, teacher completes profile on first login."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Email is required!')
            return render(request, 'auth/add_teacher.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address!')
            return render(request, 'auth/add_teacher.html')

        if faculty.objects.filter(email=email).exists():
            messages.error(request, 'A teacher with this email already exists!')
            return render(request, 'auth/add_teacher.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists!')
            return render(request, 'auth/add_teacher.html')

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Temporary password is the email itself; teacher sets their own on first login
        User.objects.create_user(username=username, email=email, password=email)
        faculty.objects.create(
            username=username, email=email,
            name='', title='', password=email,
            is_profile_complete=False,
        )
        messages.success(request, f'Teacher with email {email} added. They must complete their profile on first login.')
        return redirect(reverse('pending_registrations'))

    return render(request, 'auth/add_teacher.html')


@login_required(login_url='/log')
def complete_profile(request):
    """First-login view: teacher sets their name, title, and password."""
    try:
        teacher = faculty.objects.get(username=request.user.username)
    except faculty.DoesNotExist:
        return redirect(reverse('home'))

    if teacher.is_profile_complete:
        return redirect(reverse('home'))

    TITLE_CHOICES = [
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
    ]

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        title = request.POST.get('title', '').strip()
        new_password = request.POST.get('new_password', '').strip()

        if not all([name, title, new_password]):
            messages.error(request, 'All fields are required!')
            return render(request, 'auth/complete_profile.html', {'title_choices': TITLE_CHOICES})

        valid_titles = [t[0] for t in TITLE_CHOICES]
        if title not in valid_titles:
            messages.error(request, 'Please select a valid title.')
            return render(request, 'auth/complete_profile.html', {'title_choices': TITLE_CHOICES})

        # Update faculty record
        teacher.name = name
        teacher.title = title
        teacher.password = new_password
        teacher.is_profile_complete = True
        teacher.save()

        # Update Django user password
        request.user.set_password(new_password)
        request.user.save()

        # Re-authenticate so session stays valid after password change
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Profile completed! Welcome to EBM.')
        return redirect(reverse('home'))

    return render(request, 'auth/complete_profile.html', {'title_choices': TITLE_CHOICES})


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
