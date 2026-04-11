"""Billing models — semester bills and course bills."""

from django.db import models
from .faculty import faculty
from .academic import Session, Semester
from .course import Course


class SemesterBill(models.Model):
    """Semester-level billing roles for a faculty member."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    moderator = models.IntegerField(default=0)
    translator = models.IntegerField(default=0)
    typist = models.IntegerField(default=0)

    class Meta:
        app_label = 'root'

    def __str__(self):
        return str(str(self.session) + str(self.semester.semId) + self.teacher.name)


class courseBill(models.Model):
    """Extra invigilator/examiner assignment for a course."""
    extra = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        app_label = 'root'

    def __str__(self):
        return str(str(self.semester) + str(self.course) + str(self.extra))
