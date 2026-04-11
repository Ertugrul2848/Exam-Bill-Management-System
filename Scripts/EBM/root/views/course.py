"""Course management views."""

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
def createCourse(request, id, id2):
    """Add a new course to a semester (id=year, id2=semId). Supports Theory/Lab/Viva types."""
    session = get_object_or_404(Session, year=int(id))
    semester = get_object_or_404(Semester, session=session, semId=int(id2))
    ob = faculty.objects.filter()
    course_codes = CourseCodeMaster.objects.all()
    cont = {'ob': ob,
            'session':session.year,
            'semester':semester.semId,
            'course_codes': course_codes,
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
    return render(request, 'course/createCourse.html', cont)



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
    return render(request, 'course/viewCourse.html', cont)



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

    return render(request, 'course/updateCourse.html', cont)



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
    return render(request, 'course/addInvigilator.html', cont)



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
    return render(request, 'course/indCourse.html', cont)


@login_required(login_url='/log')
def deleteCourse(request, id, id2, id3):
    """Delete a course from a semester (id=year, id2=semId, id3=courseCode)."""
    return render(request, 'course/deleteCourse.html')



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
            if not ThesisPaper.objects.filter(session=session,semester=semester,course=course,faculty=o).exists():
                ThesisPaper(
                    session=session,semester=semester,course=course,
                    faculty=faculty.objects.get(email=o.email)
                ).save()
    ff=ThesisPaper.objects.filter(session=session,semester=semester,course=course)
    if 'delete_thesis' in request.POST:
        faculty_pk = request.POST['delete_thesis']
        ThesisPaper.objects.filter(
            session=session,semester=semester,course=course,faculty__pk=faculty_pk
        ).delete()
        return redirect(reverse('thesis', args=[id, id2, id3]))
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
        'course':course.courseCode,
        'tea':ff
    }
    return render(request,'course/thesis.html',cont)


@login_required(login_url='/log')
def supervising(request, id, id2, id3):
    """Manage thesis supervisor assignments (id=year, id2=semId, id3=courseCode)."""
    session=get_object_or_404(Session, year=int(id))
    semester=get_object_or_404(Semester, session=session,semId=int(id2))
    course=get_object_or_404(Course, session=session,semester=semester,courseCode=int(id3))
    tec=faculty.objects.filter().order_by('name')
    tea=ThesisSupervisor.objects.filter(session=session,semester=semester,course=course)
    if not tea:
        for o in tec:
            if not ThesisSupervisor.objects.filter(session=session,semester=semester,course=course,faculty=o).exists():
                ThesisSupervisor(
                    session=session,semester=semester,course=course,
                    faculty=faculty.objects.get(email=o.email)
                ).save()
    ff=ThesisSupervisor.objects.filter(session=session,semester=semester,course=course)
    if 'delete_supervisor' in request.POST:
        faculty_pk = request.POST['delete_supervisor']
        ThesisSupervisor.objects.filter(
            session=session,semester=semester,course=course,faculty__pk=faculty_pk
        ).delete()
        return redirect(reverse('supervising', args=[id, id2, id3]))
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
        'course':course.courseCode,
        'tea':ff
    }
    return render(request,'course/supervising.html',cont)

