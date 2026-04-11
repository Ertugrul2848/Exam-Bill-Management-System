"""Course management URL patterns."""

from django.urls import path
from ..views import (
    createCourse, viewCourse, updateCourse, deleteCourse,
    addInvigilator, indCourse, thesis, supervising,
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
]
