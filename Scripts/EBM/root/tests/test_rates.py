from django.test import TestCase
from django.contrib.auth.models import User
from ..models import (
    faculty, External, Session, Semester, SemesterBill, Course, courseBill,
    ThesisPaper, ThesisSupervisor,
)
from ..services import BillCalculator, get_semester_display
from .. import rates


class RatesTestCase(TestCase):
    """Tests for rates module."""

    def test_tabulation_rate_junior(self):
        self.assertEqual(rates.get_tabulation_rate(1), rates.TABULATION_RATE_JUNIOR)
        self.assertEqual(rates.get_tabulation_rate(3), rates.TABULATION_RATE_JUNIOR)

    def test_tabulation_rate_senior(self):
        self.assertEqual(rates.get_tabulation_rate(4), rates.TABULATION_RATE_SENIOR)
        self.assertEqual(rates.get_tabulation_rate(8), rates.TABULATION_RATE_SENIOR)
