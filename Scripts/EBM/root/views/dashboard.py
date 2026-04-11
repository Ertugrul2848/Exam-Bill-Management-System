"""Dashboard views."""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import faculty, Semester, Course, SemesterBill, ThesisPaper, ThesisSupervisor


@login_required(login_url='/log')
def my_assignments(request):
    """Teacher dashboard — shows all assignments and roles for the current user."""
    fac = get_object_or_404(faculty, email=request.user.email)

    chairman_of = Semester.objects.filter(chairman=fac).select_related('session')
    tabular1_of = Semester.objects.filter(tabular1=fac).select_related('session')
    tabular2_of = Semester.objects.filter(tabular2=fac).select_related('session')

    internal_courses = Course.objects.filter(internal=fac).select_related('session', 'semester')
    external_courses = Course.objects.filter(external=fac).select_related('session', 'semester')
    third_courses = Course.objects.filter(thirdExaminer=fac).select_related('session', 'semester')

    roles = SemesterBill.objects.filter(teacher=fac).select_related('semester', 'semester__session')
    moderator_roles = roles.filter(moderator=1)
    translator_roles = roles.filter(translator=1)
    typist_roles = roles.filter(typist=1)

    thesis_evals = ThesisPaper.objects.filter(faculty=fac, paperNo__gt=0).select_related('session', 'semester', 'course')
    thesis_supervising = ThesisSupervisor.objects.filter(faculty=fac, studentNo__gt=0).select_related('session', 'semester', 'course')

    return render(request, 'billing/my_assignments.html', {
        'fac': fac,
        'chairman_of': chairman_of,
        'tabular1_of': tabular1_of,
        'tabular2_of': tabular2_of,
        'internal_courses': internal_courses,
        'external_courses': external_courses,
        'third_courses': third_courses,
        'moderator_roles': moderator_roles,
        'translator_roles': translator_roles,
        'typist_roles': typist_roles,
        'thesis_evals': thesis_evals,
        'thesis_supervising': thesis_supervising,
    })
