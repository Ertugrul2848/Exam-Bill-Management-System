"""
URL configuration for the Exam Bill Management System.

This is the ROOT_URLCONF (set in settings.py). All URL patterns are defined
here in a single flat list — there is no separate EBM/urls.py.

URL Pattern Groups:
    Authentication:
        /log/              — Login page
        /accounts/login/   — Django's default login redirect (points to same view)
        /logOut/           — Logout

    Committee Management:
        /committee/        — Committee dashboard (view/create semester)
        /createCom/        — Create new exam committee
        /viewCom/<year>/   — View all semesters for a session
        /viewSem/<y>/<s>/  — View/edit a specific semester's committee
        /addRole/<y>/<s>/  — Assign moderator/translator/typist roles
        /createSem/<y>/    — Create a new semester under a session

    Course Management:
        /createCourse/<y>/<s>/       — Add course to semester
        /viewCourse/<y>/<s>/         — List all courses in a semester
        /updateCourse/<y>/<s>/<c>/   — Edit course details/examiners
        /deleteCourse/<y>/<s>/<c>/   — Delete a course
        /addInvigilator/<y>/<s>/<c>/ — Add extra invigilator to a course
        /indCourse/<y>/<s>/<c>/      — View individual course details
        /thesis/<y>/<s>/<c>/         — Manage thesis paper assignments
        /supervising/<y>/<s>/<c>/    — Manage thesis supervisor assignments

    Billing:
        /examBill/               — Teacher's own bill lookup
        /indBill/<y>/<s>/<id>/   — Individual teacher bill (with amounts)
        /pdf_view/<y>/<s>/<id>/  — PDF export of individual bill
        /examBill2/              — Chairman's semester bill lookup
        /semBill/<y>/<s>/        — List all teachers with bills in a semester
        /indBill2/<y>/<s>/<id>/  — Individual teacher bill (roles only, no amounts)

URL Parameters:
    <y> or <id>  = Session year (e.g., 2025)
    <s> or <id2> = Semester ID (1-10)
    <c> or <id3> = Course code or faculty ID (context-dependent)
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('', views.home, name='home'),
    path('accounts/login/', views.log, name="log"),
    path('log/', views.log, name="log"),
    path('logOut/', views.logOut, name="logOut"),

    # Committee management
    path('committee/', views.committee, name="committee"),
    path('createCom/', views.createCom, name="createCom"),
    path('viewCom/<int:id>/', views.viewCom, name="viewCom"),
    path('viewSem/<int:id>/<int:id2>/', views.viewSem, name="viewSem"),
    path('addRole/<int:id>/<int:id2>/', views.addRole, name="addRole"),
    path('createSem/<int:id>/', views.createSem, name="createSem"),

    # Course management
    path('createCourse/<int:id>/<int:id2>/',
         views.createCourse, name='createCourse'),
    path('viewCourse/<int:id>/<int:id2>/', views.viewCourse, name='viewCourse'),
    path('updateCourse/<int:id>/<int:id2>/<int:id3>/',
         views.updateCourse, name='updateCourse'),
    path('deleteCourse/<int:id>/<int:id2>/<int:id3>/',
         views.deleteCourse, name='deleteCourse'),
    path('addInvigilator/<int:id>/<int:id2>/<int:id3>/',
         views.addInvigilator, name='addInvigilator'),
    path('indCourse/<int:id>/<int:id2>/<int:id3>/',
         views.indCourse, name='indCourse'),
    path('thesis/<int:id>/<int:id2>/<int:id3>/', views.thesis, name="thesis"),
    path('supervising/<int:id>/<int:id2>/<int:id3>/', views.supervising, name="supervising"),

    # Billing
    path('examBill/', views.examBill, name='examBill'),
    path('indBill/<int:id>/<int:id2>/<int:id3>/', views.indBill, name='indBill'),
    path('pdf_view/<int:id>/<int:id2>/<int:id3>/', views.pdf_view, name="pdf_view"),
    path('examBill2/', views.examBill2, name='examBill2'),
    path('semBill/<int:id>/<int:id2>/', views.semBill, name='semBill'),
    path('indBill2/<int:id>/<int:id2>/<int:id3>/',
         views.indBill2, name='indBill2'),
]
