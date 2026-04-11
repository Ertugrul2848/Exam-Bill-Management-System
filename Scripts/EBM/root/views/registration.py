"""Teacher registration and chairman approval views."""

import uuid
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
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

    # Invitations: sent by chairman (no name yet), awaiting teacher to complete registration
    invitations = RegistrationRequest.objects.filter(status='pending', name='').order_by('-created_at')
    # Applications: self-registered by teacher, awaiting chairman approval
    pending = RegistrationRequest.objects.filter(status='pending').exclude(name='').order_by('-created_at')
    # Active teachers (exclude the chairman themselves)
    active_teachers = faculty.objects.filter(is_active=True).exclude(username='chairman').order_by('name')
    return render(request, 'auth/pending_registrations.html', {
        'pending': pending,
        'invitations': invitations,
        'active_teachers': active_teachers,
    })


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
    """Chairman-only: invite teacher by email — teacher completes profile via the invitation link."""
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

        # Create an invitation-only RegistrationRequest (no User yet — teacher registers via token link)
        expires_at = timezone.now() + timedelta(days=7)
        reg, created = RegistrationRequest.objects.get_or_create(
            email=email,
            defaults={
                'name': '',
                'title': '',
                'password': '',
                'status': 'pending',
                'invitation_token': uuid.uuid4(),
                'token_expires_at': expires_at,
            },
        )
        if not created:
            # Refresh token and expiry for re-invited teachers
            reg.invitation_token = uuid.uuid4()
            reg.token_expires_at = expires_at
            reg.status = 'pending'
            reg.save()

        # Build invitation link and send email
        invite_url = request.build_absolute_uri(
            reverse('register_with_token', kwargs={'token': reg.invitation_token})
        )
        send_mail(
            subject='You have been invited to join the EBM System',
            message=(
                f'Hello,\n\n'
                f'You have been invited to register as a teacher in the Exam Bill Management System.\n\n'
                f'Please click the link below to complete your registration (valid for 7 days):\n\n'
                f'{invite_url}\n\n'
                f'If you did not expect this invitation, please ignore this email.\n\n'
                f'Regards,\nEBM System'
            ),
            from_email=None,  # uses DEFAULT_FROM_EMAIL from settings
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request, f'Invitation email sent to {email}. They must complete their registration via the link.')
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


def register_with_token(request, token):
    """Public view: teacher completes registration via emailed invitation link."""
    reg = get_object_or_404(RegistrationRequest, invitation_token=token)

    # Check if token has expired
    if reg.token_expires_at and timezone.now() > reg.token_expires_at:
        messages.error(request, 'This invitation link has expired. Please ask the chairman to re-send an invitation.')
        return redirect(reverse('log'))

    # Check if already approved (link reused)
    if reg.status == 'approved':
        messages.info(request, 'This invitation has already been used. Please log in.')
        return redirect(reverse('log'))

    TITLE_CHOICES = [
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
    ]

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        title = request.POST.get('title', '').strip()
        password = request.POST.get('password', '').strip()

        if not all([name, title, password]):
            messages.error(request, 'All fields are required!')
            return render(request, 'auth/register_token.html', {'reg': reg, 'title_choices': TITLE_CHOICES})

        valid_titles = [t[0] for t in TITLE_CHOICES]
        if title not in valid_titles:
            messages.error(request, 'Please select a valid title.')
            return render(request, 'auth/register_token.html', {'reg': reg, 'title_choices': TITLE_CHOICES})

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'auth/register_token.html', {'reg': reg, 'title_choices': TITLE_CHOICES})

        if User.objects.filter(email=reg.email).exists():
            messages.error(request, 'An account with this email already exists. Please log in.')
            return redirect(reverse('log'))

        # Derive unique username from email
        username = reg.email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create Django User
        user = User.objects.create_user(username=username, email=reg.email, password=password)

        # Create faculty record
        faculty.objects.create(
            username=username,
            email=reg.email,
            name=name,
            title=title,
            password=password,
            is_profile_complete=True,
        )

        # Mark registration as approved
        reg.name = name
        reg.title = title
        reg.password = password
        reg.status = 'approved'
        reg.save()

        messages.success(request, 'Registration complete! You can now log in.')
        return redirect(reverse('log'))

    return render(request, 'auth/register_token.html', {'reg': reg, 'title_choices': TITLE_CHOICES})


@login_required(login_url='/log')
def resend_invitation(request, pk):
    """Chairman-only: regenerate the invitation token and resend the email."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    reg = get_object_or_404(RegistrationRequest, pk=pk, status='pending')

    # Regenerate token and reset expiry
    reg.invitation_token = uuid.uuid4()
    reg.token_expires_at = timezone.now() + timedelta(days=7)
    reg.save()

    # Build invitation link and resend email
    invite_url = request.build_absolute_uri(
        reverse('register_with_token', kwargs={'token': reg.invitation_token})
    )
    send_mail(
        subject='You have been invited to join the EBM System (resent)',
        message=(
            f'Hello,\n\n'
            f'Your invitation to register as a teacher in the Exam Bill Management System has been resent.\n\n'
            f'Please click the link below to complete your registration (valid for 7 days):\n\n'
            f'{invite_url}\n\n'
            f'If you did not expect this invitation, please ignore this email.\n\n'
            f'Regards,\nEBM System'
        ),
        from_email=None,
        recipient_list=[reg.email],
        fail_silently=False,
    )
    messages.success(request, f'Invitation resent to {reg.email}.')
    return redirect(reverse('pending_registrations'))


@login_required(login_url='/log')
def cancel_invitation(request, pk):
    """Chairman-only: cancel (delete) a pending invitation."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    reg = get_object_or_404(RegistrationRequest, pk=pk, status='pending')
    email = reg.email
    reg.delete()

    messages.success(request, f'Invitation for {email} has been cancelled.')
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


def accept_invitation(request):
    """Public view: teacher enters email to look up their pending invitation."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'auth/accept_invitation.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'auth/accept_invitation.html')

        reg = RegistrationRequest.objects.filter(email=email, status='pending', name='').first()
        if reg is None:
            messages.error(request, 'No pending invitation found for this email address.')
            return render(request, 'auth/accept_invitation.html')

        # Valid invitation — redirect to the token-based registration page
        return redirect(reverse('register_with_token', kwargs={'token': reg.invitation_token}))

    return render(request, 'auth/accept_invitation.html')


@login_required(login_url='/log')
def delete_teacher(request, pk):
    """Chairman-only (POST): soft-delete a teacher by deactivating their account."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    if request.method != 'POST':
        return redirect(reverse('pending_registrations'))

    teacher = get_object_or_404(faculty, pk=pk)

    # Soft-delete: deactivate faculty record and Django user
    teacher.is_active = False
    teacher.save()

    try:
        user = User.objects.get(username=teacher.username)
        user.is_active = False
        user.save()
    except User.DoesNotExist:
        pass

    messages.success(request, f'{teacher.name} has been deactivated. Their bill history is preserved.')
    return redirect(reverse('pending_registrations'))


@login_required(login_url='/log')
def transfer_chairman(request):
    """Multi-step secure transfer of chairman role to another faculty member."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    all_faculty = faculty.objects.exclude(email=request.user.email).order_by('name')

    if request.method == 'POST':
        step = request.POST.get('step')

        if step == 'confirm':
            new_email = request.POST.get('new_chairman')
            confirm_text = request.POST.get('confirm_text', '')
            if confirm_text != 'TRANSFER CHAIRMAN':
                messages.error(request, 'Please type TRANSFER CHAIRMAN to confirm')
                return render(request, 'auth/transfer_chairman.html', {
                    'faculty': all_faculty,
                    'step': 'confirm',
                    'selected': new_email,
                    'selected_name': faculty.objects.get(email=new_email).name,
                })
            return render(request, 'auth/transfer_chairman.html', {
                'faculty': all_faculty,
                'step': 'password',
                'selected': new_email,
                'selected_name': faculty.objects.get(email=new_email).name,
            })

        elif step == 'password':
            new_email = request.POST.get('new_chairman')
            password = request.POST.get('password', '')
            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password!')
                return render(request, 'auth/transfer_chairman.html', {
                    'faculty': all_faculty,
                    'step': 'password',
                    'selected': new_email,
                    'selected_name': faculty.objects.get(email=new_email).name,
                })

            # Execute transfer
            new_fac = faculty.objects.get(email=new_email)
            new_user = User.objects.get(username=new_fac.username)
            old_user = request.user

            # Give old chairman a new unique username
            temp_username = f"ex_chairman_{old_user.pk}"
            old_user.username = temp_username
            old_user.save()

            old_fac = faculty.objects.get(email=old_user.email)
            old_fac.username = temp_username
            old_fac.save()

            # Promote new chairman
            new_user.username = 'chairman'
            new_user.save()
            new_fac.username = 'chairman'
            new_fac.save()

            messages.success(request, f'Chairman role transferred to {new_fac.name}. You have been logged out.')
            from django.contrib.auth import logout
            logout(request)
            return redirect(reverse('log'))

        else:
            # Step 1: select person
            new_email = request.POST.get('new_chairman')
            if not new_email:
                messages.error(request, 'Please select a person')
                return render(request, 'auth/transfer_chairman.html', {
                    'faculty': all_faculty,
                    'step': 'select',
                })
            return render(request, 'auth/transfer_chairman.html', {
                'faculty': all_faculty,
                'step': 'confirm',
                'selected': new_email,
                'selected_name': faculty.objects.get(email=new_email).name,
            })

    return render(request, 'auth/transfer_chairman.html', {'faculty': all_faculty, 'step': 'select'})
