"""Course and thesis models."""

from django.db import models
from .faculty import faculty, External
from .academic import Session, Semester


class Course(models.Model):
    """A course offered in a specific semester."""
    COURSE_TYPE_CHOICES = [
        (1, "Theory"),
        (2, "Lab"),
        (3, "Viva"),
    ]
    courseName = models.CharField(max_length=100)
    courseCode = models.IntegerField()
    paperNo = models.IntegerField(default=0)
    internal = models.ForeignKey(
        faculty, related_name='internal', on_delete=models.CASCADE, null=True)
    external = models.ForeignKey(
        faculty, related_name='external', on_delete=models.CASCADE, null=True)
    thirdExaminer = models.ForeignKey(
        faculty, related_name='thirdExaminer', on_delete=models.CASCADE, null=True)
    tPaperNo = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    credit = models.IntegerField(null=True)
    type = models.IntegerField(choices=COURSE_TYPE_CHOICES, default=1)
    vivaExternal = models.ForeignKey(
        External, on_delete=models.CASCADE, null=True)

    class Meta:
        app_label = 'root'

    def __str__(self):
        return str(str(self.semester) + self.courseName)


class ThesisPaper(models.Model):
    """Thesis paper evaluation tracking."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    paperNo = models.IntegerField(default=0)

    class Meta:
        app_label = 'root'

    def __str__(self):
        return str(str(self.session.year) + " - " + str(self.semester.semId) + " - " + str(self.course.courseCode))


class ThesisSupervisor(models.Model):
    """Thesis supervision tracking."""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    studentNo = models.IntegerField(default=0)

    class Meta:
        app_label = 'root'

    def __str__(self):
        return str(str(self.session.year) + " - " + str(self.semester.semId) + " - " + str(self.course.courseCode))
