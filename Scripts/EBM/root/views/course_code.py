"""Course code management views — chairman/superuser only."""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from ..models import CourseCodeMaster, AcceptedCredit, Course


def _is_chairman(request):
    """Check if the current user is the chairman."""
    return User.objects.filter(username='chairman', pk=request.user.pk).exists()


@login_required(login_url='/log')
def manage_course_codes(request):
    """Chairman-only: list and add course codes."""
    if not _is_chairman(request):
        messages.error(request, 'Access Denied! Only chairman can manage course codes.')
        return redirect(reverse('home'))

    codes = CourseCodeMaster.objects.all()

    if request.method == 'POST' and 'add_code' in request.POST:
        code = request.POST.get('code', '').strip()
        name = request.POST.get('name', '').strip()
        if not code or not name:
            messages.error(request, 'Both code and name are required!')
        elif CourseCodeMaster.objects.filter(code=int(code)).exists():
            messages.error(request, f'Course code {code} already exists!')
        else:
            CourseCodeMaster.objects.create(
                code=int(code), name=name, created_by=request.user
            )
            messages.success(request, f'Course code {code} — {name} added.')
        return redirect(reverse('manage_course_codes'))

    if request.method == 'POST' and 'delete_code' in request.POST:
        code_id = request.POST.get('delete_code')
        cc = get_object_or_404(CourseCodeMaster, pk=int(code_id))
        cc.delete()
        messages.success(request, f'Course code {cc.code} deleted.')
        return redirect(reverse('manage_course_codes'))

    return render(request, 'course/manage_codes.html', {'codes': codes})


@login_required(login_url='/log')
def edit_course_code(request, pk):
    """Chairman-only: edit a course code name."""
    if not _is_chairman(request):
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    cc = get_object_or_404(CourseCodeMaster, pk=pk)

    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        if not new_name:
            messages.error(request, 'Name is required!')
        else:
            cc.name = new_name
            cc.save()
            messages.success(request, f'Course code {cc.code} updated to "{new_name}".')
        return redirect(reverse('manage_course_codes'))

    return render(request, 'course/edit_code.html', {'code': cc})


@login_required(login_url='/log')
def sync_course_name(request, pk):
    """Chairman-only: sync course name to/from master."""
    if not _is_chairman(request):
        messages.error(request, 'Access Denied!')
        return redirect(reverse('home'))

    cc = get_object_or_404(CourseCodeMaster, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('sync_action')
        if action == 'to_master':
            # Update master from a course's current name
            new_name = request.POST.get('course_name', '').strip()
            if new_name and new_name != cc.name:
                cc.name = new_name
                cc.save()
                messages.success(request, f'Master updated: {cc.code} → "{new_name}"')
        elif action == 'from_master':
            # Update all courses with this code to master name
            updated = Course.objects.filter(courseCode=cc.code).update(courseName=cc.name)
            messages.success(request, f'Synced {updated} course(s) to master name "{cc.name}"')

    return redirect(reverse('manage_course_codes'))


@login_required(login_url='/log')
def manage_credits(request):
    """Chairman-only: list, add, and delete accepted course credit values."""
    if not _is_chairman(request):
        messages.error(request, 'Access Denied! Only chairman can manage accepted credits.')
        return redirect(reverse('home'))

    credits = AcceptedCredit.objects.all()

    if request.method == 'POST' and 'add_credit' in request.POST:
        value = request.POST.get('value', '').strip()
        if not value:
            messages.error(request, 'Credit value is required!')
        else:
            try:
                int_val = int(value)
                if int_val <= 0:
                    raise ValueError
                if AcceptedCredit.objects.filter(value=int_val).exists():
                    messages.error(request, f'Credit {int_val} already exists!')
                else:
                    AcceptedCredit.objects.create(value=int_val)
                    messages.success(request, f'Credit {int_val} added.')
            except ValueError:
                messages.error(request, 'Credit value must be a positive integer.')
        return redirect(reverse('manage_credits'))

    if request.method == 'POST' and 'delete_credit' in request.POST:
        credit_id = request.POST.get('delete_credit')
        ac = get_object_or_404(AcceptedCredit, pk=int(credit_id))
        ac.delete()
        messages.success(request, f'Credit {ac.value} deleted.')
        return redirect(reverse('manage_credits'))

    return render(request, 'course/manage_credits.html', {'credits': credits})


@login_required(login_url='/log')
def course_code_api(request):
    """JSON API: return course codes for dropdown auto-fill."""
    codes = CourseCodeMaster.objects.all().values('code', 'name')
    return JsonResponse(list(codes), safe=False)
