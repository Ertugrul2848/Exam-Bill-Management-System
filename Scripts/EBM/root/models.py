"""
Database models for the Exam Bill Management System.

This module defines all Django models used to manage university examination
processes including faculty profiles, academic sessions, semester committees,
courses, billing records, and thesis tracking.

Model Relationships:
    Session → Semester → Course → courseBill
    Session → Semester → SemesterBill
    Session → Semester → Course → ThesisPaper
    Session → Semester → Course → ThesisSupervisor
    faculty → (used across all models as examiner/committee roles)
    External → (used in Semester and Course as external examiner)
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group, User


class faculty(models.Model):
    """
    Faculty member (teacher/instructor) profile.

    Each faculty member has a corresponding Django User account for authentication.
    The `password` field stores a plaintext copy used by the custom login flow
    (the actual auth password is managed by Django's User model).

    Attributes:
        username: Matches the Django User.username for authentication lookup.
        email: Primary identifier used for login and faculty selection in forms.
        name: Full display name of the faculty member.
        title: Academic title (e.g., Professor, Associate Professor).
        password: Plaintext password used by the custom login view (legacy).
    """
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    password = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return str(self.email)


class External(models.Model):
    """
    External examiner profile.

    External examiners are non-faculty members who participate in exam
    committees and viva examinations. They are separate from the faculty
    model because they don't have system login credentials.

    Attributes:
        name: Full display name of the external examiner.
        email: Email address used as identifier in forms.
    """
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Session(models.Model):
    """
    Academic session (year).

    Represents a single academic year. Uses the year as the primary key
    (e.g., 2024, 2025). All semesters, courses, and bills are tied to a session.

    Attributes:
        year: The academic year (e.g., 2025). Serves as the primary key.
    """
    year = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(1900)],
    )

    def __str__(self):
        return str(self.year)


class Semester(models.Model):
    """
    Semester within an academic session, including its exam committee.

    Each semester has an exam committee consisting of a chairman, two tabulators,
    and one external examiner. The semId maps to a specific year-semester
    combination (see SEMESTER_CHOICES).

    Attributes:
        semId: Semester identifier (1-10), maps to year/semester via SEMESTER_CHOICES.
        session: The academic session this semester belongs to.
        chairman: Faculty member who chairs the exam committee (one-to-one).
        tabular1: First tabulator on the exam committee.
        tabular2: Second tabulator on the exam committee.
        external: External examiner on the committee.
    """
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
        """Return human-readable semester name (e.g., '1st Year 1st Semester')."""
        return self.get_semId_display()

    def __str__(self):
        return str(str(self.session) + " " + str(self.semId))


class SemesterBill(models.Model):
    """
    Semester-level billing roles for a faculty member.

    Tracks whether a faculty member holds a special semester-wide role
    (moderator, translator, or typist/stencil-cutter) for a given semester.
    Each role is stored as an integer flag (0=no, 1=yes).

    One SemesterBill record is created per faculty member per semester
    when a committee is formed.

    Attributes:
        session: The academic session.
        semester: The semester this bill belongs to.
        teacher: The faculty member.
        moderator: 1 if the teacher is a moderator, 0 otherwise.
        translator: 1 if the teacher is a translator, 0 otherwise.
        typist: 1 if the teacher is a stencil-cutter/typist, 0 otherwise.
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    moderator = models.IntegerField(default=0)
    translator = models.IntegerField(default=0)
    typist = models.IntegerField(default=0)

    def __str__(self):
        return str(str(self.session) + str(self.semester.semId) + self.teacher.name)


class Course(models.Model):
    """
    A course offered in a specific semester.

    Courses can be one of three types: Theory (1), Lab (2), or Viva (3).
    Each type has different examiner roles and billing rules.

    Theory courses have: internal examiner, external examiner, third examiner.
    Lab courses have: internal examiner, external examiner, optional invigilators.
    Viva courses have: external examiner (from External model), optional participants.

    Attributes:
        courseName: Name of the course (e.g., 'Data Structures').
        courseCode: Numeric course code (e.g., 201).
        paperNo: Number of exam papers to evaluate (for theory/lab billing).
        internal: Internal faculty examiner.
        external: External faculty examiner (not the External model — this is a faculty member).
        thirdExaminer: Third examiner for theory courses (handles overflow papers).
        tPaperNo: Number of papers assigned to the third examiner.
        duration: Duration in hours (used for lab/viva billing calculations).
        session: The academic session this course belongs to.
        semester: The semester this course belongs to.
        credit: Course credit hours.
        type: Course type — 1=Theory, 2=Lab, 3=Viva (see COURSE_TYPE_CHOICES).
        vivaExternal: External examiner from the External model (for viva courses).
    """
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
        return str(str(self.semester) + self.courseName)


class courseBill(models.Model):
    """
    Extra invigilator/examiner assignment for a course.

    Used to assign additional faculty members to lab invigilator or viva-voce
    roles beyond the standard internal/external examiners. Each record
    represents one extra faculty assignment for a specific course.

    Attributes:
        extra: The additional faculty member assigned to this course.
        session: The academic session.
        semester: The semester.
        course: The course this extra assignment belongs to.
    """
    extra = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return str(str(self.semester) + str(self.course) + str(self.extra))


class ThesisPaper(models.Model):
    """
    Thesis paper evaluation tracking.

    Records how many thesis papers a faculty member has evaluated for a
    specific course in a semester. Used for billing calculations.

    Attributes:
        session: The academic session.
        semester: The semester.
        course: The thesis course.
        faculty: The faculty member evaluating papers.
        paperNo: Number of papers evaluated by this faculty member.
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    paperNo = models.IntegerField(default=0)

    def __str__(self):
        return str(str(self.session.year) + " - " + str(self.semester.semId) + " - " + str(self.course.courseCode))


class ThesisSupervisor(models.Model):
    """
    Thesis supervision tracking.

    Records how many students a faculty member is supervising for a
    specific thesis course in a semester. Used for billing calculations.

    Attributes:
        session: The academic session.
        semester: The semester.
        course: The thesis course.
        faculty: The supervising faculty member.
        studentNo: Number of students supervised by this faculty member.
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    faculty = models.ForeignKey(faculty, on_delete=models.CASCADE, null=True)
    studentNo = models.IntegerField(default=0)

    def __str__(self):
        return str(str(self.session.year) + " - " + str(self.semester.semId) + " - " + str(self.course.courseCode))
