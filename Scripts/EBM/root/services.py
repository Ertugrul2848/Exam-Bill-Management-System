"""
Bill calculation service for exam bill management.
"""
from dataclasses import dataclass

from .models import (
    faculty, Session, Semester, SemesterBill, Course, courseBill,
    ThesisPaper, ThesisSupervisor,
)
from . import rates


@dataclass
class BillItem:
    """A single line item in a faculty member's bill."""
    role: str
    course_code: int
    course_name: str
    paper_no: int
    duration: int
    bill: int = 0
    st: int = 0
    teacher: str = ''


class BillCalculator:
    """Calculates examination bills for a faculty member in a given semester."""

    def __init__(self, session_year, sem_id, fac):
        self.session = Session.objects.get(year=int(session_year))
        self.semester = Semester.objects.get(session=self.session, semId=int(sem_id))
        self.fac = fac
        self.courses = Course.objects.filter(session=self.session, semester=self.semester)
        self.sem_bills = SemesterBill.objects.filter(session=self.session, semester=self.semester)
        self.thesis_papers = ThesisPaper.objects.filter(session=self.session, semester=self.semester)
        self.thesis_supervisors = ThesisSupervisor.objects.filter(session=self.session, semester=self.semester)
        # Prefetch all courseBill records to avoid N+1 queries in course role methods
        self.course_bills = courseBill.objects.filter(session=self.session, semester=self.semester)

    def calculate(self, include_amounts=True):
        """
        Calculate all bill items for the faculty member.

        Args:
            include_amounts: If True, include bill amounts (for indBill/pdf_view).
                           If False, omit amounts (for indBill2/cal).
        """
        items = []
        items.extend(self._committee_roles(include_amounts))
        items.extend(self._thesis_roles(include_amounts))
        items.extend(self._semester_roles(include_amounts))
        items.extend(self._course_roles(include_amounts))
        return items

    def calculate_total(self):
        """Calculate total bill amount."""
        items = self.calculate(include_amounts=True)
        return sum(item.bill for item in items)

    def _committee_roles(self, include_amounts):
        items = []
        if self.semester.chairman == self.fac:
            items.append(BillItem(
                role="Chairman", course_code=0, course_name="CSE",
                paper_no=0, duration=0,
                bill=rates.CHAIRMAN_RATE if include_amounts else 0,
                teacher=self.fac.email,
            ))
        if self.semester.tabular1 == self.fac or self.semester.tabular2 == self.fac:
            amount = rates.get_tabulation_rate(self.semester.semId) if include_amounts else 0
            items.append(BillItem(
                role="Tabulation", course_code=0, course_name="CSE",
                paper_no=0, duration=0, bill=amount,
                teacher=self.fac.email,
            ))
        return items

    def _thesis_roles(self, include_amounts):
        items = []
        for tp in self.thesis_papers:
            if tp.faculty == self.fac and tp.paperNo > 0:
                items.append(BillItem(
                    role="Thesis Paper Evaluation",
                    course_code=tp.course.courseCode, course_name="CSE",
                    paper_no=tp.paperNo, duration=0,
                    bill=tp.paperNo * rates.THESIS_PAPER_EVALUATION_PER_PAPER if include_amounts else 0,
                    teacher=self.fac.email,
                ))
        for ts in self.thesis_supervisors:
            if ts.faculty == self.fac and ts.studentNo > 0:
                items.append(BillItem(
                    role="Thesis Supervisor",
                    course_code=ts.course.courseCode, course_name="CSE",
                    paper_no=ts.studentNo, duration=0,
                    bill=ts.studentNo * rates.THESIS_SUPERVISOR_PER_STUDENT if include_amounts else 0,
                    teacher=self.fac.email,
                ))
        return items

    def _semester_roles(self, include_amounts):
        items = []
        num_courses = len(self.courses) - 1
        for sb in self.sem_bills:
            if sb.teacher != self.fac:
                continue
            if sb.moderator == 1:
                items.append(BillItem(
                    role="Moderation", course_code=0, course_name="CSE",
                    paper_no=num_courses, duration=0,
                    bill=rates.MODERATION_RATE if include_amounts else 0,
                    teacher=self.fac.email,
                ))
            if sb.translator == 1:
                items.append(BillItem(
                    role="Translation", course_code=0, course_name="CSE",
                    paper_no=num_courses, duration=0,
                    bill=rates.TRANSLATION_RATE if include_amounts else 0,
                    teacher=self.fac.email,
                ))
            if sb.typist == 1:
                items.append(BillItem(
                    role="Stencil-Cutter", course_code=0, course_name="CSE",
                    paper_no=num_courses, duration=0,
                    bill=rates.STENCIL_CUTTER_RATE if include_amounts else 0,
                    teacher=self.fac.email,
                ))
        return items

    def _course_roles(self, include_amounts):
        items = []
        for c in self.courses:
            if c.type == 1:
                items.extend(self._theory_course_roles(c, include_amounts))
            elif c.type == 2:
                items.extend(self._lab_course_roles(c, include_amounts))
            elif c.type == 3:
                items.extend(self._viva_course_roles(c, include_amounts))
        return items

    def _theory_course_roles(self, course, include_amounts):
        items = []
        # Question Paper Formulation
        if course.internal == self.fac:
            items.append(BillItem(
                role="Question-Paper Formulation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=0, duration=0,
                bill=rates.QUESTION_PAPER_FORMULATION_RATE if include_amounts else 0,
                st=1, teacher=self.fac.email,
            ))
        if course.external == self.fac:
            items.append(BillItem(
                role="Question-Paper Formulation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=0, duration=0,
                bill=rates.QUESTION_PAPER_FORMULATION_RATE if include_amounts else 0,
                st=1, teacher=self.fac.email,
            ))
        # Paper Evaluation
        if course.internal == self.fac:
            items.append(BillItem(
                role="Paper Evaluation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=course.paperNo, duration=0,
                bill=course.paperNo * rates.PAPER_EVALUATION_PER_PAPER if include_amounts else 0,
                teacher=self.fac.email,
            ))
        if course.external == self.fac:
            items.append(BillItem(
                role="Paper Evaluation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=course.paperNo, duration=0,
                bill=course.paperNo * rates.PAPER_EVALUATION_PER_PAPER if include_amounts else 0,
                teacher=self.fac.email,
            ))
        if course.thirdExaminer == self.fac:
            items.append(BillItem(
                role="Paper Evaluation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=course.tPaperNo, duration=0,
                bill=course.tPaperNo * rates.PAPER_EVALUATION_PER_PAPER if include_amounts else 0,
                teacher=self.fac.email,
            ))
        return items

    def _lab_course_roles(self, course, include_amounts):
        items = []
        if course.internal == self.fac or course.external == self.fac:
            items.append(BillItem(
                role="Lab Evaluation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=course.paperNo, duration=course.duration,
                bill=rates.LAB_EVALUATION_RATE if include_amounts else 0,
                teacher=self.fac.email,
            ))
            items.append(BillItem(
                role="Lab Viva",
                course_code=course.courseCode, course_name="CSE",
                paper_no=0, duration=course.duration,
                bill=course.duration * rates.LAB_VIVA_PER_HOUR if include_amounts else 0,
                teacher=self.fac.email,
            ))
        extras = [cb for cb in self.course_bills if cb.course_id == course.id]
        for ex in extras:
            if ex.extra == self.fac:
                items.append(BillItem(
                    role="Lab Invigilator",
                    course_code=course.courseCode, course_name="CSE",
                    paper_no=0, duration=course.duration,
                    bill=course.duration * rates.LAB_INVIGILATOR_PER_HOUR if include_amounts else 0,
                    teacher=self.fac.email,
                ))
        return items

    def _viva_course_roles(self, course, include_amounts):
        items = []
        extras = [cb for cb in self.course_bills if cb.course_id == course.id]
        for ex in extras:
            if ex.extra == self.fac:
                items.append(BillItem(
                    role="Viva-Voce",
                    course_code=course.courseCode, course_name="CSE",
                    paper_no=0, duration=course.duration,
                    bill=course.duration * rates.VIVA_VOCE_PER_HOUR if include_amounts else 0,
                    teacher=self.fac.email,
                ))
        return items


def get_semester_display(sem_id):
    """Convert semester ID to human-readable string."""
    year = int((sem_id + 1) / 2)
    year_labels = {1: "1st Year", 2: "2nd Year", 3: "3rd Year", 4: "4th Year", 5: "Masters"}

    # Determine 1st or 2nd semester within the year
    sem_in_year = 1 if sem_id % 2 == 1 else 2
    sem_labels = {1: "1st Semester", 2: "2nd Semester"}

    year_str = year_labels.get(year, f"{year}th Year")
    sem_str = sem_labels.get(sem_in_year, f"{sem_in_year}th Semester")

    return f"{year_str} {sem_str}"
