"""Moderator role management views."""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..models import faculty, Semester, ModeratorRole


def _is_chairman(user):
    return User.objects.filter(username='chairman', pk=user.pk).exists()


@login_required(login_url='/log')
def manage_moderators(request):
    """List all moderator roles and add new ones."""
    if not _is_chairman(request.user):
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    moderators = ModeratorRole.objects.select_related('user', 'semester').order_by('-created_at')
    teachers = faculty.objects.all().order_by('name')
    semesters = Semester.objects.select_related('session').order_by('-session__year', 'semId')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        scope = request.POST.get('scope')
        semester_id = request.POST.get('semester') or None

        if not teacher_id or not scope:
            messages.error(request, 'Teacher and scope are required.')
            return redirect(reverse('manage_moderators'))

        teacher = get_object_or_404(faculty, pk=teacher_id)
        semester = get_object_or_404(Semester, pk=semester_id) if semester_id else None

        if scope == 'semester' and not semester:
            messages.error(request, 'A semester must be selected for semester-scoped moderators.')
            return redirect(reverse('manage_moderators'))

        if ModeratorRole.objects.filter(user=teacher, semester=semester).exists():
            messages.error(request, f'{teacher.name} already has a moderator role for this scope.')
            return redirect(reverse('manage_moderators'))

        ModeratorRole.objects.create(
            user=teacher,
            assigned_by=request.user,
            scope=scope,
            semester=semester,
        )
        messages.success(request, f'{teacher.name} added as {scope} moderator.')
        return redirect(reverse('manage_moderators'))

    return render(request, 'auth/manage_moderators.html', {
        'moderators': moderators,
        'teachers': teachers,
        'semesters': semesters,
    })


@login_required(login_url='/log')
def edit_moderator(request, pk):
    """Toggle permissions for an existing moderator role."""
    if not _is_chairman(request.user):
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    role = get_object_or_404(ModeratorRole, pk=pk)

    if request.method == 'POST':
        role.can_create_semester = 'can_create_semester' in request.POST
        role.can_view_semester_bill = 'can_view_semester_bill' in request.POST
        role.can_view_all_bills = 'can_view_all_bills' in request.POST
        role.can_view_session_bills = 'can_view_session_bills' in request.POST
        role.can_approve_requests = 'can_approve_requests' in request.POST
        role.view_only = 'view_only' in request.POST
        role.save()
        messages.success(request, f'Permissions updated for {role.user.name}.')
        return redirect(reverse('manage_moderators'))

    return render(request, 'auth/edit_moderator.html', {'role': role})


@login_required(login_url='/log')
def remove_moderator(request, pk):
    """Delete a moderator role."""
    if not _is_chairman(request.user):
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    role = get_object_or_404(ModeratorRole, pk=pk)
    name = role.user.name
    role.delete()
    messages.success(request, f'Moderator role removed for {name}.')
    return redirect(reverse('manage_moderators'))
