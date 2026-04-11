"""
Bill calculation service for the Exam Bill Management System.

This module centralizes all examination bill calculation logic that was
previously duplicated across 4 view functions (indBill, pdf_view, cal, indBill2).

Architecture:
    BillCalculator — Main service class. Given a session, semester, and faculty
    member, it computes all bill line items across committee roles, thesis roles,
    semester roles, and course-specific roles (theory/lab/viva).

    BillItem — Dataclass representing a single line item in a bill.

    get_semester_display() — Utility to convert a semester ID (1-10) into a
    human-readable label like "2nd Year 1st Semester".

Usage:
    from root.services import BillCalculator, get_semester_display

    calc = BillCalculator(session_year=2025, sem_id=3, fac=faculty_obj)
    items = calc.calculate(include_amounts=True)   # Full bill with amounts
    items = calc.calculate(include_amounts=False)   # Role list only (no amounts)
    total = calc.calculate_total()                  # Sum of all bill amounts

Rate constants are defined in root/rates.py — this module imports them
rather than hardcoding values.
"""

from dataclasses import dataclass

from .models import (
    faculty, Session, Semester, SemesterBill, Course, courseBill,
    ThesisPaper, ThesisSupervisor,
)
from . import rates


@dataclass
class BillItem:
    """
    A single line item in a faculty member's examination bill.

    Attributes:
        role: Description of the role (e.g., 'Chairman', 'Paper Evaluation').
        course_code: Numeric course code (0 for semester-wide roles).
        course_name: Department name (currently hardcoded to 'CSE').
        paper_no: Number of papers involved (0 if not applicable).
        duration: Duration in hours (used for lab/viva roles, 0 otherwise).
        bill: Calculated bill amount in BDT (0 when include_amounts=False).
        st: Legacy field used by some templates (1 for question paper roles).
        teacher: Email of the faculty member (used by semBill summary view).
    """
    role: str
    course_code: int
    course_name: str
    paper_no: int
    duration: int
    bill: int = 0
    st: int = 0
    teacher: str = ''


class BillCalculator:
    """
    Calculates all examination bill items for a faculty member in a given semester.

    The calculator queries all relevant data (courses, semester bills, thesis
    records) once in __init__, then the calculate() method iterates through
    each role type to build a list of BillItem objects.

    Bill categories (checked in order):
        1. Committee roles — Chairman, Tabulation
        2. Thesis roles — Paper Evaluation, Supervision
        3. Semester roles — Moderation, Translation, Stencil-Cutter
        4. Course roles — Theory (Q-Paper, Evaluation), Lab (Eval, Viva,
           Invigilator), Viva-Voce

    Args:
        session_year: Academic year (int or str, e.g., 2025).
        sem_id: Semester ID (int or str, 1-10).
        fac: faculty model instance for the target faculty member.
    """

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
            include_amounts: If True, compute bill amounts using rates.py constants.
                If False, set all bill amounts to 0 (used by summary views that
                only need to know which roles a faculty member holds).

        Returns:
            List of BillItem objects representing each billing line item.
        """
        items = []
        items.extend(self._committee_roles(include_amounts))
        items.extend(self._thesis_roles(include_amounts))
        items.extend(self._semester_roles(include_amounts))
        items.extend(self._course_roles(include_amounts))
        return items

    def calculate_total(self):
        """Calculate and return the total bill amount (sum of all items)."""
        items = self.calculate(include_amounts=True)
        return sum(item.bill for item in items)

    def _committee_roles(self, include_amounts):
        """Check if faculty is chairman or tabulator for this semester."""
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
        """Check if faculty has thesis paper evaluation or supervision roles."""
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
        """Check if faculty holds moderator, translator, or typist roles."""
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
        """Dispatch to type-specific handlers for each course."""
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
        """
        Bill items for theory courses.

        Theory examiners are billed for:
        - Question-Paper Formulation (flat rate per course, for internal & external)
        - Paper Evaluation (per-paper rate, for internal, external & third examiner)
        """
        items = []
        # Question Paper Formulation — internal examiner
        if course.internal == self.fac:
            items.append(BillItem(
                role="Question-Paper Formulation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=0, duration=0,
                bill=rates.QUESTION_PAPER_FORMULATION_RATE if include_amounts else 0,
                st=1, teacher=self.fac.email,
            ))
        # Question Paper Formulation — external examiner
        if course.external == self.fac:
            items.append(BillItem(
                role="Question-Paper Formulation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=0, duration=0,
                bill=rates.QUESTION_PAPER_FORMULATION_RATE if include_amounts else 0,
                st=1, teacher=self.fac.email,
            ))
        # Paper Evaluation — internal examiner (uses course.paperNo)
        if course.internal == self.fac:
            items.append(BillItem(
                role="Paper Evaluation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=course.paperNo, duration=0,
                bill=course.paperNo * rates.PAPER_EVALUATION_PER_PAPER if include_amounts else 0,
                teacher=self.fac.email,
            ))
        # Paper Evaluation — external examiner (uses course.paperNo)
        if course.external == self.fac:
            items.append(BillItem(
                role="Paper Evaluation",
                course_code=course.courseCode, course_name="CSE",
                paper_no=course.paperNo, duration=0,
                bill=course.paperNo * rates.PAPER_EVALUATION_PER_PAPER if include_amounts else 0,
                teacher=self.fac.email,
            ))
        # Paper Evaluation — third examiner (uses course.tPaperNo for both count and billing)
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
        """
        Bill items for lab courses.

        Lab examiners (internal/external) are billed for:
        - Lab Evaluation (flat rate)
        - Lab Viva (per-hour rate)

        Additional invigilators (from courseBill) are billed for:
        - Lab Invigilator (per-hour rate)
        """
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
        # Check extra invigilators (from prefetched course_bills)
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
        """
        Bill items for viva courses.

        Viva participants (from courseBill extra assignments) are billed
        at a per-hour rate.
        """
        items = []
        # Check extra participants (from prefetched course_bills)
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
    """
    Convert a semester ID (1-10) to a human-readable string.

    Mapping:
        1 → "1st Year 1st Semester"    6 → "3rd Year 2nd Semester"
        2 → "1st Year 2nd Semester"    7 → "4th Year 1st Semester"
        3 → "2nd Year 1st Semester"    8 → "4th Year 2nd Semester"
        4 → "2nd Year 2nd Semester"    9 → "Masters 1st Semester"
        5 → "3rd Year 1st Semester"   10 → "Masters 2nd Semester"

    Args:
        sem_id: Integer semester identifier (1-10).

    Returns:
        Human-readable string like "2nd Year 1st Semester".
    """
    year = int((sem_id + 1) / 2)
    year_labels = {1: "1st Year", 2: "2nd Year", 3: "3rd Year", 4: "4th Year", 5: "Masters"}

    # Determine 1st or 2nd semester within the year
    sem_in_year = 1 if sem_id % 2 == 1 else 2
    sem_labels = {1: "1st Semester", 2: "2nd Semester"}

    year_str = year_labels.get(year, f"{year}th Year")
    sem_str = sem_labels.get(sem_in_year, f"{sem_in_year}th Semester")

    return f"{year_str} {sem_str}"
