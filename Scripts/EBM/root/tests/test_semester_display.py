from django.test import TestCase
from django.contrib.auth.models import User
from ..models import (
    faculty, External, Session, Semester, SemesterBill, Course, courseBill,
    ThesisPaper, ThesisSupervisor,
)
from ..services import BillCalculator, get_semester_display
from .. import rates


class GetSemesterDisplayTestCase(TestCase):
    """Tests for get_semester_display helper."""

    def test_first_year_first_semester(self):
        result = get_semester_display(1)
        self.assertIn('1st', result)

    def test_fourth_year_second_semester(self):
        result = get_semester_display(8)
        self.assertIn('4th Year', result)
        self.assertIn('2nd Semester', result)

    def test_second_year_first_semester(self):
        result = get_semester_display(3)
        self.assertIn('2nd Year', result)
        self.assertIn('1st Semester', result)

    def test_masters(self):
        result = get_semester_display(9)
        self.assertIn('Masters', result)
        self.assertIn('1st Semester', result)
