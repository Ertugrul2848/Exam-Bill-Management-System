"""Billing views."""

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
def examBill(request):
    """Teacher's own bill lookup. Enter session/semester to view personal bill."""
    if request.method == 'POST':
        session_year = int(request.POST['session'])
        if session_year < 1900:
            messages.error(request, 'Session year must be 1900 or later!')
            return render(request, 'billing/examBill.html')
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
    return render(request, 'billing/examBill.html')



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
    return render(request, 'billing/indBill.html', cont)


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
    template_path = 'billing/pdf_view.html'
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
            return render(request, 'billing/examBill2.html')
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
    return render(request, 'billing/examBill2.html')



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
    return render(request, 'billing/semBill.html', cont)



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
    return render(request, 'billing/indBill.html', cont)
