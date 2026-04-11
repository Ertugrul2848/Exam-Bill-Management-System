"""Committee management views."""

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
def committee(request):
    """Committee dashboard. Allows viewing an existing session or creating a new semester."""
    if 'sess' in request.POST or 'sem' in request.POST:
        session_val = request.POST.get('session', '').strip()
        if not session_val:
            messages.error(request, 'Please select a session!')
        else:
            sess = int(session_val)
            if sess < 1900:
                messages.error(request, 'Session year must be 1900 or later!')
            else:
                ob = Session.objects.filter(year=sess)
                if not ob:
                    messages.error(request, 'Session Does not Exist !!')
                else:
                    if 'sess' in request.POST:
                        return redirect(reverse('viewCom', args=[sess]))
                    else:
                        return redirect(reverse('createSem', args=[sess]))
    sessions = Session.objects.all().order_by('-year')
    current_year = datetime.now().year
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    return render(request, 'committee/committee.html', {
        'sessions': sessions,
        'current_year': current_year,
        'is_chairman': is_chairman,
    })



@login_required(login_url='/log')
def createCom(request):
    """
    Create a new exam committee. Chairman-only access.

    Creates a Session (if new), a Semester with committee members,
    and a SemesterBill record for every faculty member.
    """
    cont = None
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied !!!')
    else:
        # Filter out faculty already serving as chairman in any semester
        existing_chairmen_emails = Semester.objects.values_list('chairman__email', flat=True)
        available_faculty = faculty.objects.exclude(email__in=existing_chairmen_emails).order_by('name')
        all_faculty = faculty.objects.all().order_by('name')
        oc = External.objects.filter()
        cont = {
            'ob': all_faculty,
            'available_chairmen': available_faculty,
            'oc': oc,
            'current_year': datetime.now().year,
            'semester_choices': Semester.SEMESTER_CHOICES,
        }
        if request.method == 'POST':
            session_year = int(request.POST['session'])
            if session_year < 1900:
                messages.error(request, 'Session year must be 1900 or later!')
                return render(request, 'committee/createCom.html', cont)
            oo = Session.objects.filter(year=session_year)
            if not oo:
                aa = Session(year=session_year)
                aa.save()
            ca = Session.objects.get(year=session_year)
            aa = Semester.objects.filter(
                session=ca, semId=int(request.POST['year']))
            if not aa:
                selected_chairman = faculty.objects.get(email=request.POST['chairman'])
                sob = Semester.objects.filter(session=ca)
                flag = False
                for o in sob:
                    if o.chairman == selected_chairman:
                        flag = True
                if flag:
                    messages.error(
                        request, "Chairman Already Exists in another Committee !")
                else:
                    tea1 = faculty.objects.get(email=request.POST['tabular1'])
                    tea2 = faculty.objects.get(email=request.POST['tabular2'])
                    tea3 = External.objects.get(email=request.POST['external'])
                    flag = False
                    if tea1 == tea2 or tea2 == selected_chairman or tea1 == selected_chairman:
                        flag = True
                    if flag:
                        messages.error(
                            request, 'Faculty can not be selected more than once !!')
                    else:
                        bb = Semester(semId=int(
                            request.POST['year']), session=ca, chairman=selected_chairman, tabular1=tea1, tabular2=tea2, external=tea3)
                        bb.save()
                        for o in all_faculty:
                            tea = faculty.objects.get(email=o.email)
                            aa = SemesterBill(
                                session=ca, semester=bb, teacher=tea)
                            aa.save()
                        messages.success(
                            request, "Committee Created Successfully")
            else:
                messages.error(
                    request, "Semester Already Exists !!")
    return render(request, 'committee/createCom.html', cont)



@login_required(login_url='/log')
def viewCom(request, id):
    """List all semesters for a given session year (id=year)."""
    session = get_object_or_404(Session, year=int(id))
    show_archived = request.GET.get('show_archived', '0') == '1'
    if show_archived:
        semester = Semester.objects.filter(session=session).order_by('semId')
    else:
        semester = Semester.objects.filter(session=session, is_archived=False).order_by('semId')
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    ar = [{'qd': o, 'st': o.get_display_name()} for o in semester]
    cont = {
        'ob': ar,
        'session': id,
        'show_archived': show_archived,
        'is_chairman': is_chairman,
    }
    return render(request, 'committee/viewCom.html', cont)



@login_required(login_url='/log')
def viewSem(request, id, id2):
    """View/edit semester committee. Chairman can update members and assign roles (id=year, id2=semId)."""
    ob = faculty.objects.get(email=request.user.email)
    oc = faculty.objects.filter()
    od = External.objects.filter()
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    moderator = SemesterBill.objects.filter(
        session=session, semester=semester, moderator=1)
    typist = SemesterBill.objects.filter(
        session=session, semester=semester, typist=1)
    translator = SemesterBill.objects.filter(
        session=session, semester=semester, translator=1)
    flag = False
    if ob == semester.chairman or (semester.acting_chairman and ob == semester.acting_chairman):
        flag = True
    # Build filtered teacher list — exclude teachers who already have ANY role
    all_role_emails = set()
    all_role_emails.update(sb.teacher.email for sb in moderator)
    all_role_emails.update(sb.teacher.email for sb in translator)
    all_role_emails.update(sb.teacher.email for sb in typist)
    available_teachers = oc.exclude(email__in=all_role_emails).order_by('name')

    cont = {
        'sem': semester,
        'flag': flag,
        'ob': oc,
        'oc': od,
        'moderator': moderator,
        'typist': typist,
        'translator': translator,
        'available_teachers': available_teachers,
        'session_id': id,
        'sem_id': id2,
    }

    if 'update' in request.POST:
        tea1 = faculty.objects.get(email=request.POST['tabular1'])
        tea2 = faculty.objects.get(email=request.POST['tabular2'])
        tea3 = External.objects.get(email=request.POST['external'])
        flag = False

        if tea1 == tea2 or tea1 == semester.chairman or tea2 == semester.chairman:
            flag = True
        if flag:
            messages.error(
                request, 'Faculty can not be selected more than once !!')
        else:
            semester.tabular1 = faculty.objects.get(
                email=request.POST.get('tabular1'))
            semester.tabular2 = faculty.objects.get(
                email=request.POST.get('tabular2'))
            semester.external = External.objects.get(
                email=request.POST.get('external'))
            semester.save()
            messages.success(
                request, 'Committee Updated Successfully !')
    if 'add_role' in request.POST:
        tea = faculty.objects.get(email=request.POST['teacher'])
        role_val = request.POST['role']
        sb, created = SemesterBill.objects.get_or_create(
            session=session, semester=semester, teacher=tea)
        # Check if teacher already has ANY role in this semester
        if sb.moderator == 1 or sb.translator == 1 or sb.typist == 1:
            messages.error(request, f'{tea.name} already has a role in this semester!')
        elif role_val == "1":
            sb.moderator = 1
            sb.save()
            messages.success(request, f'{tea.name} added as Moderator')
        elif role_val == "2":
            sb.translator = 1
            sb.save()
            messages.success(request, f'{tea.name} added as Translator')
        elif role_val == "3":
            sb.typist = 1
            sb.save()
            messages.success(request, f'{tea.name} added as Stencil-Cutter')
        return redirect(reverse('viewSem', args=[id, id2]))
    if 'add' in request.POST:
        return redirect(reverse('addRole', args=[id, id2]))
    if 'moderator' in request.POST:
        mod = faculty.objects.get(email=request.POST.get('moderator'))
        oc = SemesterBill.objects.get(
            session=session, semester=semester, teacher=mod)
        oc.moderator = 0
        oc.save()
        return redirect(reverse('viewSem', args=[id, id2]))
    if 'translator' in request.POST:
        mod = faculty.objects.get(email=request.POST.get('translator'))
        oc = SemesterBill.objects.get(
            session=session, semester=semester, teacher=mod)
        oc.translator = 0
        oc.save()
        return redirect(reverse('viewSem', args=[id, id2]))
    if 'typist' in request.POST:
        mod = faculty.objects.get(email=request.POST.get('typist'))
        oc = SemesterBill.objects.get(
            session=session, semester=semester, teacher=mod)
        oc.typist = 0
        oc.save()
        return redirect(reverse('viewSem', args=[id, id2]))
    return render(request, 'committee/viewSem.html', cont)



@login_required(login_url='/log')
def addRole(request, id, id2):
    """Assign moderator/translator/typist role to a faculty member (id=year, id2=semId)."""
    ob = faculty.objects.filter()
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    tea = faculty.objects.get(email=request.user.email)
    chairman = semester.chairman
    flag = False
    if chairman == tea:
        flag = True
    cont = {'ob': ob,
            'flag': flag
            }
    if request.method == 'POST':
        session = get_object_or_404(Session, year=int(id))
        semester = get_object_or_404(Semester, session=session, semId=int(id2))
        oo = SemesterBill.objects.filter(session=session, semester=semester)
        tea = faculty.objects.get(email=request.POST['teacher'])
        oa = SemesterBill.objects.filter(
            session=session, semester=semester, teacher=tea)
        if not oa:
            no = SemesterBill(session=session, semester=semester, teacher=tea)
            no.save()
        ca = SemesterBill.objects.get(
            session=session, semester=semester, teacher=tea)
        val = request.POST['role']
        if val == "1":
            if ca.moderator == 1:
                messages.error(request, 'This teacher is already a moderator!')
            else:
                ca.moderator = 1
                ca.save()
        elif val == "2":
            if ca.translator == 1:
                messages.error(request, 'This teacher is already a translator!')
            else:
                ca.translator = 1
                ca.save()
        elif val == "3":
            if ca.typist == 1:
                messages.error(request, 'This teacher is already a stencil-cutter!')
            else:
                ca.typist = 1
                ca.save()
        return redirect(reverse('viewSem', args=[id, id2]))
    return render(request, 'committee/addRole.html', cont)



@login_required(login_url='/log')
def assign_acting_chairman(request, id, id2):
    """Assign an acting chairman to a semester. Chairman-only (id=year, id2=semId)."""
    ob = get_object_or_404(faculty, email=request.user.email)
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    if ob != semester.chairman:
        messages.error(request, 'Access Denied !!!')
        return redirect(reverse('viewSem', args=[id, id2]))
    if request.method == 'POST':
        selected_email = request.POST.get('acting_chairman', '').strip()
        if not selected_email:
            messages.error(request, 'Please select a faculty member.')
        else:
            selected_faculty = get_object_or_404(faculty, email=selected_email)
            semester.acting_chairman = selected_faculty
            semester.save()
            messages.success(request, f'{selected_faculty.name} assigned as Acting Chairman.')
    return redirect(reverse('viewSem', args=[id, id2]))


@login_required(login_url='/log')
def remove_acting_chairman(request, id, id2):
    """Remove the acting chairman from a semester. Chairman-only (id=year, id2=semId)."""
    ob = get_object_or_404(faculty, email=request.user.email)
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    if ob != semester.chairman:
        messages.error(request, 'Access Denied !!!')
        return redirect(reverse('viewSem', args=[id, id2]))
    if request.method == 'POST':
        semester.acting_chairman = None
        semester.save()
        messages.success(request, 'Acting Chairman removed.')
    return redirect(reverse('viewSem', args=[id, id2]))


@login_required(login_url='/log')
def toggle_archive(request, id, id2):
    """Toggle archive status of a semester. Chairman-only."""
    is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    if not is_chairman:
        messages.error(request, 'Access Denied!')
        return redirect(reverse('viewCom', args=[id]))
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    semester.is_archived = not semester.is_archived
    semester.save()
    status = 'archived' if semester.is_archived else 'unarchived'
    messages.success(request, f'Semester {semester.get_display_name()} {status}.')
    show = '1' if request.GET.get('show_archived') == '1' else '0'
    return redirect(f"{reverse('viewCom', args=[id])}?show_archived={show}")


@login_required(login_url='/log')
def createSem(request, id):
    """Display semester creation options for a session (id=year)."""
    session = get_object_or_404(Session, year=int(id))
    semester = Semester.objects.filter(session=session)
    ar = [{'qd': o, 'st': o.get_display_name()} for o in semester]
    cont = {
        'ob': ar,
        'session': id
    }
    return render(request, 'committee/createSem.html', cont)



