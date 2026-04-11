"""Course management URL patterns."""

from django.urls import path
from ..views import (
    createCourse, viewCourse, updateCourse, deleteCourse,
    addInvigilator, indCourse, thesis, supervising,
    manage_course_codes, edit_course_code, sync_course_name, course_code_api,
    manage_credits,
)

urlpatterns = [
    path('createCourse/<int:id>/<int:id2>/', createCourse, name='createCourse'),
    path('viewCourse/<int:id>/<int:id2>/', viewCourse, name='viewCourse'),
    path('updateCourse/<int:id>/<int:id2>/<int:id3>/', updateCourse, name='updateCourse'),
    path('deleteCourse/<int:id>/<int:id2>/<int:id3>/', deleteCourse, name='deleteCourse'),
    path('addInvigilator/<int:id>/<int:id2>/<int:id3>/', addInvigilator, name='addInvigilator'),
    path('indCourse/<int:id>/<int:id2>/<int:id3>/', indCourse, name='indCourse'),
    path('thesis/<int:id>/<int:id2>/<int:id3>/', thesis, name="thesis"),
    path('supervising/<int:id>/<int:id2>/<int:id3>/', supervising, name="supervising"),
    path('course-codes/', manage_course_codes, name='manage_course_codes'),
    path('course-codes/<int:pk>/edit/', edit_course_code, name='edit_course_code'),
    path('course-codes/<int:pk>/sync/', sync_course_name, name='sync_course_name'),
    path('api/course-codes/', course_code_api, name='course_code_api'),
    path('credits/', manage_credits, name='manage_credits'),
]
