from django.db import models
from django.contrib.auth.models import Group, User
class faculty(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=True,null=True)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    password = models.CharField(max_length=15, blank=True)
    def __str__(self):
        return str(self.email)


class External(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Session(models.Model):
    year = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.year)


class Semester(models.Model):
    SEMESTER_CHOICES = [
        (1, "1st Year 1st Semester"),
        (2, "1st Year 2nd Semester"),
        (3, "2nd Year 1st Semester"),
        (4, "2nd Year 2nd Semester"),
        (5, "3rd Year 1st Semester"),
        (6, "3rd Year 2nd Semester"),
        (7, "4th Year 1st Semester"),
        (8, "4th Year 2nd Semester"),
        (9, "Masters 1st Semester"),
        (10, "Masters 2nd Semester"),
    ]
    semId = models.IntegerField(choices=SEMESTER_CHOICES)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    chairman = models.OneToOneField(
        faculty, related_name='chairman', on_delete=models.CASCADE)
    tabular1 = models.ForeignKey(
        faculty, related_name="tabular1", on_delete=models.CASCADE)
    tabular2 = models.ForeignKey(
        faculty, related_name="tabular2", on_delete=models.CASCADE)
    external = models.ForeignKey(External, on_delete=models.CASCADE)

    def get_display_name(self):
        return self.get_semId_display()

    def __str__(self):
        return str(str(self.session)+" "+str(self.semId))


class SemesterBill(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    moderator = models.IntegerField(default=0)
    translator = models.IntegerField(default=0)
    typist = models.IntegerField(default=0)

    def __str__(self):
        return str(str(self.session)+str(self.semester.semId)+self.teacher.name)


class Course(models.Model):
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
    def __str__(self):
        return str(str(self.semester)+self.courseName)


class courseBill(models.Model):
    extra = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return str(str(self.semester)+str(self.course)+str(self.extra))
class ThesisPaper(models.Model):
    session=models.ForeignKey(Session,on_delete=models.CASCADE,null=True)
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE,null=True)
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True)
    faculty=models.ForeignKey(faculty,on_delete=models.CASCADE,null=True)
    paperNo=models.IntegerField(default=0)
    def __str__(self):
        return str(str(self.session.year)+" - "+str(self.semester.semId)+" - "+str(self.course.courseCode))
class ThesisSupervisor(models.Model):
    session=models.ForeignKey(Session,on_delete=models.CASCADE,null=True)
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE,null=True)
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True)
    faculty=models.ForeignKey(faculty,on_delete=models.CASCADE,null=True)
    studentNo=models.IntegerField(default=0)
    def __str__(self):
        return str(str(self.session.year)+" - "+str(self.semester.semId)+" - "+str(self.course.courseCode))   