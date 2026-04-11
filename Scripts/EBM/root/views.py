"""
Views for the Exam Bill Management System.

This module contains all view functions organized into four groups:

Authentication Views:
    home        — Landing page (requires login)
    log         — Login page (email + password)
    logOut      — Logout and redirect to login

Committee Management Views:
    committee   — Dashboard: view existing or create new semester
    createCom   — Create exam committee (chairman-only)
    viewCom     — List all semesters in a session
    viewSem     — View/edit semester committee details and roles
    addRole     — Assign moderator/translator/typist to a faculty member
    createSem   — Create new semester with courses

Course Management Views:
    createCourse    — Add a new course to a semester
    viewCourse      — List courses in a semester
    updateCourse    — Edit course examiners and details
    deleteCourse    — Remove a course
    addInvigilator  — Assign extra invigilator to a lab/viva course
    indCourse       — View individual course details
    thesis          — Manage thesis paper evaluation assignments
    supervising     — Manage thesis supervision assignments

Billing Views:
    examBill    — Teacher's own bill lookup form
    indBill     — Individual teacher bill with amounts (uses BillCalculator)
    pdf_view    — PDF export of individual teacher bill (uses BillCalculator)
    examBill2   — Chairman's semester-wide bill lookup form
    semBill     — List all teachers with bills in a semester (uses BillCalculator)
    indBill2    — Individual teacher bill without amounts (uses BillCalculator)

URL Parameters Convention:
    id  = Session year (e.g., 2025)
    id2 = Semester ID (1-10)
    id3 = Course code or faculty ID (context-dependent)
"""

from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from xhtml2pdf import pisa
from .models import *
from .services import BillCalculator, get_semester_display

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


@login_required(login_url='/log')
def committee(request):
    """Committee dashboard. Allows viewing an existing session or creating a new semester."""
    if 'sess' in request.POST:
        sess = int(request.POST['session'])
        if sess < 1900:
            messages.error(request, 'Session year must be 1900 or later!')
        else:
            ob = Session.objects.filter(year=sess)
            if not ob:
                messages.error(request, 'Session Does not Exist !!')
            else:
                return redirect(reverse('viewCom', args=[sess]))
    if 'sem' in request.POST:
        sess = int(request.POST['session'])
        if sess < 1900:
            messages.error(request, 'Session year must be 1900 or later!')
        else:
            ob = Session.objects.filter(year=sess)
            if not ob:
                messages.error(request, 'Session Does not Exist !!')
            else:
                return redirect(reverse('createSem', args=[sess]))
    sessions = Session.objects.all().order_by('-year')
    current_year = datetime.now().year
    return render(request, 'committee.html', {
        'sessions': sessions,
        'current_year': current_year,
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
        ob = faculty.objects.filter()
        oc = External.objects.filter()
        cont = {
            'ob': ob,
            'oc': oc,
            'current_year': datetime.now().year,
            'semester_choices': Semester.SEMESTER_CHOICES,
        }
        if request.method == 'POST':
            session_year = int(request.POST['session'])
            if session_year < 1900:
                messages.error(request, 'Session year must be 1900 or later!')
                return render(request, 'createCom.html', cont)
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
                        for o in ob:
                            tea = faculty.objects.get(email=o.email)
                            aa = SemesterBill(
                                session=ca, semester=bb, teacher=tea)
                            aa.save()
                        messages.success(
                            request, "Committee Created Successfully")
            else:
                messages.error(
                    request, "Semester Already Exists !!")
    return render(request, 'createCom.html', cont)


@login_required(login_url='/log')
def viewCom(request, id):
    """List all semesters for a given session year (id=year)."""
    session = get_object_or_404(Session, year=int(id))
    semester = Semester.objects.filter(session=session).order_by('semId')
    ar = [{'qd': o, 'st': o.get_display_name()} for o in semester]
    cont = {
        'ob': ar,
        'session': id
    }
    return render(request, 'viewCom.html', cont)


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
    if ob == semester.chairman:
        flag = True
    cont = {
        'sem': semester,
        'flag': flag,
        'ob': oc,
        'oc': od,
        'moderator': moderator,
        'typist': typist,
        'translator': translator
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
    return render(request, 'viewSem.html', cont)


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
    return render(request, 'addRole.html', cont)


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
    return render(request, 'createSem.html', cont)


@login_required(login_url='/log')
def createCourse(request, id, id2):
    """Add a new course to a semester (id=year, id2=semId). Supports Theory/Lab/Viva types."""
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    ob = faculty.objects.filter()
    cont = {'ob': ob,
            'session':session.year,
            'semester':semester.semId
            }
    if request.method == 'POST':
        name = request.POST['name']
        code = request.POST['code']
        code = int(code)
        credit = request.POST['credit']
        credit = int(code)
        type = request.POST['type']
        type = int(type)
        if type == 1 or type == 2:
            internal = faculty.objects.get(email=request.POST['internal'])
            external = faculty.objects.get(email=request.POST['external'])
        course = Course.objects.filter(
            session=session, semester=semester, courseCode=int(code))
        if not course:
            if type == 1 or type == 2:
                oa = Course(session=session, semester=semester, courseName=name, courseCode=code, credit=credit,
                            type=type, internal=internal, external=external)
                oa.save()
            else:
                oa = Course(session=session, semester=semester,
                            courseName=name, courseCode=code, credit=credit, type=type)
                oa.save()
            messages.success(
                request, 'Course Created Successfully !!')
        else:
            messages.error(request, 'Course Already Exists')
    return render(request, 'createCourse.html', cont)


@login_required(login_url='/log')
def viewCourse(request, id, id2):
    """List all courses in a semester with add/update/delete actions (id=year, id2=semId)."""
    tea = faculty.objects.get(email=request.user.email)
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    course = Course.objects.filter(session=session, semester=semester)
    flag = False
    if tea == semester.chairman:
        flag = True
    cont = {"ob": course,
            'flag': flag,
            'session': id,
            'semester': id2
            }
    if 'add' in request.POST:
        return redirect(reverse('createCourse', args=[id, id2]))
    if 'update' in request.POST:
        return redirect(reverse('updateCourse', args=[id, id2, request.POST['update']]))
    if 'delete' in request.POST:
        co = get_object_or_404(Course, session=session, semester=semester, courseCode=int(request.POST['delete']))
        co.delete()
        return redirect(reverse('viewCourse', args=[id, id2]))
    return render(request, 'viewCourse.html', cont)


@login_required(login_url='/log')
def updateCourse(request, id, id2, id3):
    """Edit course examiners and details (id=year, id2=semId, id3=courseCode)."""
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    ob = faculty.objects.filter()
    theory = False
    lab = False
    viva = False
    course = get_object_or_404(Course, session=session, semester=semester, courseCode=int(id3))
    extra = courseBill.objects.filter(
        session=session, semester=semester, course=course)

    if course.type == 1:
        theory = True
    elif course.type == 2:
        lab = True
    elif course.type == 3:
        viva = True
    ex = External.objects.filter()
    cont = {
        'session':id,
        'semester':id2,
        'id3':id3,
        'ob': ob,
        'theory': theory,
        'lab': lab,
        'viva': viva,
        'course': course,
        'extra': extra,
        'ex': ex
    }
    if 'theory' in request.POST:
        internal = faculty.objects.get(email=request.POST.get('internal'))
        external = faculty.objects.get(email=request.POST.get('external'))
        third = faculty.objects.get(email=request.POST.get('third'))
        paperNo = request.POST['paperNo']
        tPaperNo = request.POST['tpaperNo']
        course.internal = internal
        course.external = external
        course.thirdExaminer = third
        course.paperNo = paperNo
        course.tPaperNo = tPaperNo
        course.save()
        return redirect(reverse('viewCourse', args=[id, id2]))
    if 'lab' in request.POST:
        internal = faculty.objects.get(email=request.POST.get('internal'))
        external = faculty.objects.get(email=request.POST.get('external'))
        duration = request.POST['duration']
        course.internal = internal
        course.external = external
        course.duration = duration
        course.save()
        return redirect(reverse('viewCourse', args=[id, id2]))
    if 'viva' in request.POST:
        external = External.objects.get(email=request.POST.get('external'))
        duration = request.POST['duration']
        course.vivaExternal = external
        course.duration = duration
        course.save()
        return redirect(reverse('viewCourse', args=[id, id2]))
    if 'invigilator' in request.POST:
        return redirect(reverse('addInvigilator', args=[id, id2, id3]))

    return render(request, 'updateCourse.html', cont)


@login_required(login_url='/log')
def addInvigilator(request, id, id2, id3):
    """Assign an extra invigilator to a lab/viva course (id=year, id2=semId, id3=courseCode)."""
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    course = get_object_or_404(Course, session=session, semester=semester, courseCode=int(id3))
    ob = faculty.objects.filter()
    ex = External.objects.filter()
    cont = {'ob': ob, }
    if 'add' in request.POST:
        tea = faculty.objects.get(email=request.POST['invigilator'])
        oo = courseBill(session=session, semester=semester,
                        course=course, extra=tea)
        oo.save()
        return redirect(reverse('updateCourse', args=[id, id2, id3]))
    return render(request, 'addInvigilator.html', cont)


@login_required(login_url='/log')
def indCourse(request, id, id2, id3):
    """View individual course details and examiners (id=year, id2=semId, id3=courseCode)."""
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    course = get_object_or_404(Course, session=session, semester=semester, courseCode=int(id3))
    theory = False
    viva = False
    lab = False
    if course.type == 1:
        theory = True
    if course.type == 2:
        lab = True
    if course.type == 3:
        viva = True
    extra = courseBill.objects.filter(
        session=session, semester=semester, course=course)

    cont = {
        'course': course,
        'theory': theory,
        'viva': viva,
        'lab': lab,
        'extra': extra
    }
    return render(request, 'indCourse.html', cont)
@login_required(login_url='/log')
def deleteCourse(request, id, id2, id3):
    """Delete a course from a semester (id=year, id2=semId, id3=courseCode)."""
    return render(request, 'deleteCourse.html')


@login_required(login_url='/log')
def examBill(request):
    """Teacher's own bill lookup. Enter session/semester to view personal bill."""
    if request.method == 'POST':
        session_year = int(request.POST['session'])
        if session_year < 1900:
            messages.error(request, 'Session year must be 1900 or later!')
            return render(request, 'examBill.html')
        session = Session.objects.filter(year=session_year)
        flag = False
        if not session:
            flag = True
        else:
            session = Session.objects.get(year=int(request.POST['session']))
            semester = Semester.objects.filter(
                session=session, semId=int(request.POST['semester']))
            if not semester:
                flag = True
        if flag:
            messages.error(
                request, 'Session Or Semester Does not Exist !!')
        else:
            return redirect(reverse('indBill', args=[request.POST['session'], request.POST['semester'], request.user.id]))
    return render(request, 'examBill.html')


@login_required(login_url='/log')
def indBill(request, id, id2, id3):
    """Individual teacher bill with amounts (id=year, id2=semId, id3=facultyId). Uses BillCalculator."""
    fac = faculty.objects.get(email=request.user.email)
    calc = BillCalculator(id, id2, fac)
    ar = calc.calculate(include_amounts=True)
    total = sum(item.bill for item in ar)
    ss = get_semester_display(int(id2))
    cont = {
        'ob': ar,
        'name': fac,
        'session': id,
        'ss': ss,
        'total': total
    }
    if 'pdf' in request.POST:
        res = reverse('pdf_view', args=[id, id2, id3])
        return redirect(res)
    return render(request, 'indBill.html', cont)
@login_required(login_url='/log')
def pdf_view(request, id, id2, id3):
    """Generate PDF export of individual teacher bill (id=year, id2=semId, id3=facultyId). Uses xhtml2pdf."""
    fac = faculty.objects.get(email=request.user.email)
    calc = BillCalculator(id, id2, fac)
    ar = calc.calculate(include_amounts=True)
    total = sum(item.bill for item in ar)
    ss = get_semester_display(int(id2))
    cont = {
        'ob': ar,
        'name': fac,
        'session': id,
        'ss': ss,
        'total': total
    }
    template_path = 'pdf_view.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ' filename="bill.pdf"'
    template = get_template(template_path)
    html = template.render(cont)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required(login_url='/log')
def examBill2(request):
    """Chairman's semester-wide bill lookup. Only chairman can access semester bills."""
    if request.method == 'POST':
        session_year = int(request.POST['session'])
        if session_year < 1900:
            messages.error(request, 'Session year must be 1900 or later!')
            return render(request, 'examBill2.html')
        session = Session.objects.filter(year=session_year)
        flag = False
        if not session:
            flag = True
        else:
            session = Session.objects.get(year=int(request.POST['session']))
            semester = Semester.objects.filter(
                session=session, semId=int(request.POST['semester']))
            if not semester:
                flag = True
        if flag:
            messages.error(
                request, 'Session Or Semester Does not Exist !!')
        else:
            ca = faculty.objects.get(email=request.user.email)
            da = faculty.objects.get(email="chairman@gmail.com")
            semester = Semester.objects.get(
                session=session, semId=int(request.POST['semester']))
            if not (ca == semester.chairman or da == ca):
                flag = True
            if flag:
                messages.error(request, 'Access Denied !!')
            else:
                return redirect(reverse('semBill', args=[request.POST['session'], request.POST['semester']]))
    return render(request, 'examBill2.html')


@login_required(login_url='/log')
def semBill(request, id, id2):
    """List all faculty with billing roles in a semester (id=year, id2=semId). Uses BillCalculator."""
    all_faculty = faculty.objects.filter()
    ob = []
    for f in all_faculty:
        calc = BillCalculator(id, id2, f)
        items = calc.calculate(include_amounts=False)
        if len(items) > 0:
            ob.append(f)
    ss = get_semester_display(int(id2))
    cont = {
        'ob': ob,
        'semester': ss
    }
    if request.method == 'POST':
        aa = request.POST.get('teacher')
        oo = faculty.objects.get(email=aa)
        return redirect(reverse('indBill2', args=[id, id2, oo.id]))
    return render(request, 'semBill.html', cont)


@login_required(login_url='/log')
def indBill2(request, id, id2, id3):
    """Individual teacher bill — roles only, no amounts (id=year, id2=semId, id3=facultyId). Uses BillCalculator."""
    fac = get_object_or_404(faculty, id=int(id3))
    calc = BillCalculator(id, id2, fac)
    ar = calc.calculate(include_amounts=False)
    ss = get_semester_display(int(id2))
    cont = {
        'ob': ar,
        'name': fac,
        'session': id,
        'ss': ss
    }
    return render(request, 'indBill.html', cont)
@login_required(login_url='/log')
def thesis(request, id, id2, id3):
    """Manage thesis paper evaluation assignments (id=year, id2=semId, id3=courseCode)."""
    session=get_object_or_404(Session, year=int(id))
    semester=get_object_or_404(Semester, session=session,semId=int(id2))
    course=get_object_or_404(Course, session=session,semester=semester,courseCode=int(id3))
    tec=faculty.objects.filter().order_by('name')
    tea=ThesisPaper.objects.filter(session=session,semester=semester,course=course)
    if not tea:
        for o in tec:
            cc=ThesisPaper(
                session=session,semester=semester,course=course,
                faculty=faculty.objects.get(email=o.email)
            )
            cc.save()
    ff=ThesisPaper.objects.filter(session=session,semester=semester,course=course)
    if 'save' in request.POST:
        for o,i in zip(request.POST.getlist('paper'),ff):
            dd=ThesisPaper.objects.get(
                session=session,semester=semester,course=course,
                faculty=faculty.objects.get(email=i.faculty.email)
            )
            dd.paperNo=int(o)
            dd.save()
        res = reverse('updateCourse', args=[id, id2, id3])
        return redirect(res)
    if 'cancel' in request.POST:
        res = reverse('updateCourse', args=[id, id2, id3])
        return redirect(res)

    cont={

        'session':session.year,
        'semester':semester.semId,
        'tea':ff
    }
    return render(request,'thesis.html',cont)
def supervising(request, id, id2, id3):
    """Manage thesis supervisor assignments (id=year, id2=semId, id3=courseCode)."""
    session=get_object_or_404(Session, year=int(id))
    semester=get_object_or_404(Semester, session=session,semId=int(id2))
    course=get_object_or_404(Course, session=session,semester=semester,courseCode=int(id3))
    tec=faculty.objects.filter().order_by('name')
    tea=ThesisSupervisor.objects.filter(session=session,semester=semester,course=course)
    if not tea:
        for o in tec:
            cc=ThesisSupervisor(
                session=session,semester=semester,course=course,
                faculty=faculty.objects.get(email=o.email)
            )
            cc.save()
    ff=ThesisSupervisor.objects.filter(session=session,semester=semester,course=course)
    if 'save' in request.POST:
        for o,i in zip(request.POST.getlist('student'),ff):
            dd=ThesisSupervisor.objects.get(
                session=session,semester=semester,course=course,
                faculty=faculty.objects.get(email=i.faculty.email)
            )
            dd.studentNo=int(o)
            dd.save()
        res = reverse('updateCourse', args=[id, id2, id3])
        return redirect(res)
    if 'cancel' in request.POST:
        res = reverse('updateCourse', args=[id, id2, id3])
        return redirect(res)

    cont={

        'session':session.year,
        'semester':semester.semId,
        'tea':ff
    }
    return render(request,'supervising.html',cont)