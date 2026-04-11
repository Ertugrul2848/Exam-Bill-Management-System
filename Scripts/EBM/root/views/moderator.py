"""Moderator role management views."""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..models import faculty, Semester, ModeratorRole


def _is_chairman_or_semester_chair(user):
    """Return 'system' if user is system chairman, 'semester' if semester chairman, else None."""
    if User.objects.filter(username='chairman', pk=user.pk).exists():
        return 'system'
    fac = faculty.objects.filter(email=user.email).first()
    if fac and Semester.objects.filter(chairman=fac).exists():
        return 'semester'
    return None


def _get_chaired_semesters(user):
    """Return Semester queryset for semesters this user chairs (as faculty)."""
    fac = faculty.objects.filter(email=user.email).first()
    if not fac:
        return Semester.objects.none()
    return Semester.objects.filter(chairman=fac).select_related('session')


# Keep old helper for backward compatibility with any other callers
def _is_chairman(user):
    return _is_chairman_or_semester_chair(user) == 'system'


@login_required(login_url='/log')
def manage_moderators(request):
    """List all moderator roles and add new ones."""
    role_type = _is_chairman_or_semester_chair(request.user)
    if not role_type:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    is_system = role_type == 'system'
    chaired_semesters = _get_chaired_semesters(request.user) if not is_system else None

    if is_system:
        moderators = ModeratorRole.objects.select_related('user', 'semester').order_by('-created_at')
        semesters = Semester.objects.select_related('session').order_by('-session__year', 'semId')
    else:
        chaired_semester_pks = list(chaired_semesters.values_list('pk', flat=True))
        moderators = ModeratorRole.objects.filter(
            semester__in=chaired_semester_pks
        ).select_related('user', 'semester').order_by('-created_at')
        semesters = chaired_semesters.order_by('-session__year', 'semId')

    teachers = faculty.objects.all().order_by('name')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        semester_id = request.POST.get('semester') or None

        if not teacher_id:
            messages.error(request, 'Teacher is required.')
            return redirect(reverse('manage_moderators'))

        # Semester chairmen can only add semester-scoped moderators
        if is_system:
            scope = request.POST.get('scope')
            if not scope:
                messages.error(request, 'Scope is required.')
                return redirect(reverse('manage_moderators'))
        else:
            scope = 'semester'

        teacher = get_object_or_404(faculty, pk=teacher_id)
        semester = get_object_or_404(Semester, pk=semester_id) if semester_id else None

        if scope == 'semester' and not semester:
            messages.error(request, 'A semester must be selected for semester-scoped moderators.')
            return redirect(reverse('manage_moderators'))

        # Semester chairman can only add moderators to their own semesters
        if not is_system and semester:
            chaired_pks = list(_get_chaired_semesters(request.user).values_list('pk', flat=True))
            if semester.pk not in chaired_pks:
                messages.error(request, 'You can only add moderators for semesters you chair.')
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
        'is_system': is_system,
    })


@login_required(login_url='/log')
def edit_moderator(request, pk):
    """Toggle permissions for an existing moderator role."""
    role_type = _is_chairman_or_semester_chair(request.user)
    if not role_type:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    role = get_object_or_404(ModeratorRole, pk=pk)

    # Semester chairman can only edit roles within their semesters
    if role_type == 'semester':
        chaired_pks = list(_get_chaired_semesters(request.user).values_list('pk', flat=True))
        if not role.semester or role.semester.pk not in chaired_pks:
            messages.error(request, 'You can only edit moderators for semesters you chair.')
            return redirect(reverse('manage_moderators'))

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
    """Delete a moderator role. Requires POST."""
    role_type = _is_chairman_or_semester_chair(request.user)
    if not role_type:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    if request.method != 'POST':
        return redirect(reverse('manage_moderators'))

    role = get_object_or_404(ModeratorRole, pk=pk)

    # Semester chairman can only remove roles within their semesters
    if role_type == 'semester':
        chaired_pks = list(_get_chaired_semesters(request.user).values_list('pk', flat=True))
        if not role.semester or role.semester.pk not in chaired_pks:
            messages.error(request, 'You can only remove moderators for semesters you chair.')
            return redirect(reverse('manage_moderators'))

    name = role.user.name
    role.delete()
    messages.success(request, f'Moderator role removed for {name}.')
    return redirect(reverse('manage_moderators'))
