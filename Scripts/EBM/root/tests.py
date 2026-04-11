from django.test import TestCase
from django.contrib.auth.models import User

from .models import (
    faculty, External, Session, Semester, SemesterBill, Course, courseBill,
    ThesisPaper, ThesisSupervisor,
)
from .services import BillCalculator, get_semester_display
from . import rates


class BillCalculatorTestCase(TestCase):
    """Tests for BillCalculator service class."""

    @classmethod
    def setUpTestData(cls):
        # Create faculty members
        cls.chairman_fac = faculty.objects.create(
            username='chairman', email='chairman@test.com',
            name='Dr. Chairman', title='Professor', password='test123',
        )
        cls.tab1_fac = faculty.objects.create(
            username='tab1', email='tab1@test.com',
            name='Dr. Tab1', title='Associate Professor', password='test123',
        )
        cls.tab2_fac = faculty.objects.create(
            username='tab2', email='tab2@test.com',
            name='Dr. Tab2', title='Assistant Professor', password='test123',
        )
        cls.internal_fac = faculty.objects.create(
            username='internal', email='internal@test.com',
            name='Dr. Internal', title='Professor', password='test123',
        )
        cls.external_fac = faculty.objects.create(
            username='external_fac', email='externalfac@test.com',
            name='Dr. External', title='Professor', password='test123',
        )
        cls.extra_fac = faculty.objects.create(
            username='extra', email='extra@test.com',
            name='Dr. Extra', title='Lecturer', password='test123',
        )

        # Create external examiner
        cls.ext = External.objects.create(
            name='External Examiner', email='ext@test.com',
        )

        # Create session and semester
        cls.session = Session.objects.create(year=2025)
        cls.semester = Semester.objects.create(
            semId=1, session=cls.session,
            chairman=cls.chairman_fac,
            tabular1=cls.tab1_fac,
            tabular2=cls.tab2_fac,
            external=cls.ext,
        )

        # Create semester bills
        SemesterBill.objects.create(
            session=cls.session, semester=cls.semester,
            teacher=cls.chairman_fac, moderator=1, translator=0, typist=0,
        )
        SemesterBill.objects.create(
            session=cls.session, semester=cls.semester,
            teacher=cls.internal_fac, moderator=0, translator=1, typist=0,
        )

        # Create a theory course (type=1)
        cls.theory_course = Course.objects.create(
            courseName='Data Structures', courseCode=201,
            paperNo=100, tPaperNo=20, duration=0,
            session=cls.session, semester=cls.semester,
            credit=3, type=1,
            internal=cls.internal_fac, external=cls.external_fac,
            thirdExaminer=cls.extra_fac,
        )

        # Create a lab course (type=2)
        cls.lab_course = Course.objects.create(
            courseName='Data Structures Lab', courseCode=202,
            paperNo=50, tPaperNo=0, duration=3,
            session=cls.session, semester=cls.semester,
            credit=1, type=2,
            internal=cls.internal_fac, external=cls.external_fac,
        )

        # Create a viva course (type=3)
        cls.viva_course = Course.objects.create(
            courseName='Thesis Viva', courseCode=400,
            paperNo=0, tPaperNo=0, duration=2,
            session=cls.session, semester=cls.semester,
            credit=3, type=3,
            vivaExternal=cls.ext,
        )

        # Add extra invigilator for lab
        courseBill.objects.create(
            session=cls.session, semester=cls.semester,
            course=cls.lab_course, extra=cls.extra_fac,
        )

        # Add extra for viva
        courseBill.objects.create(
            session=cls.session, semester=cls.semester,
            course=cls.viva_course, extra=cls.extra_fac,
        )

        # Create thesis records
        ThesisPaper.objects.create(
            session=cls.session, semester=cls.semester,
            course=cls.theory_course, faculty=cls.internal_fac, paperNo=5,
        )
        ThesisSupervisor.objects.create(
            session=cls.session, semester=cls.semester,
            course=cls.theory_course, faculty=cls.internal_fac, studentNo=3,
        )

    def test_chairman_bill(self):
        calc = BillCalculator(2025, 1, self.chairman_fac)
        items = calc.calculate(include_amounts=True)
        chairman_items = [i for i in items if i.role == 'Chairman']
        self.assertEqual(len(chairman_items), 1)
        self.assertEqual(chairman_items[0].bill, rates.CHAIRMAN_RATE)

    def test_tabulation_junior_rate(self):
        calc = BillCalculator(2025, 1, self.tab1_fac)
        items = calc.calculate(include_amounts=True)
        tab_items = [i for i in items if i.role == 'Tabulation']
        self.assertEqual(len(tab_items), 1)
        self.assertEqual(tab_items[0].bill, rates.TABULATION_RATE_JUNIOR)

    def test_moderation_role(self):
        calc = BillCalculator(2025, 1, self.chairman_fac)
        items = calc.calculate(include_amounts=True)
        mod_items = [i for i in items if i.role == 'Moderation']
        self.assertEqual(len(mod_items), 1)
        self.assertEqual(mod_items[0].bill, rates.MODERATION_RATE)

    def test_translation_role(self):
        calc = BillCalculator(2025, 1, self.internal_fac)
        items = calc.calculate(include_amounts=True)
        trans_items = [i for i in items if i.role == 'Translation']
        self.assertEqual(len(trans_items), 1)
        self.assertEqual(trans_items[0].bill, rates.TRANSLATION_RATE)

    def test_theory_internal_examiner(self):
        calc = BillCalculator(2025, 1, self.internal_fac)
        items = calc.calculate(include_amounts=True)
        qp_items = [i for i in items if i.role == 'Question-Paper Formulation' and i.course_code == 201]
        pe_items = [i for i in items if i.role == 'Paper Evaluation' and i.course_code == 201]
        self.assertEqual(len(qp_items), 1)
        self.assertEqual(qp_items[0].bill, rates.QUESTION_PAPER_FORMULATION_RATE)
        self.assertEqual(len(pe_items), 1)
        self.assertEqual(pe_items[0].bill, 100 * rates.PAPER_EVALUATION_PER_PAPER)

    def test_theory_external_examiner(self):
        calc = BillCalculator(2025, 1, self.external_fac)
        items = calc.calculate(include_amounts=True)
        qp_items = [i for i in items if i.role == 'Question-Paper Formulation']
        self.assertEqual(len(qp_items), 1)

    def test_third_examiner(self):
        calc = BillCalculator(2025, 1, self.extra_fac)
        items = calc.calculate(include_amounts=True)
        pe_items = [i for i in items if i.role == 'Paper Evaluation' and i.course_code == 201]
        self.assertEqual(len(pe_items), 1)
        # Third examiner uses tPaperNo for paper_no but paperNo for bill calculation
        self.assertEqual(pe_items[0].paper_no, 20)

    def test_lab_evaluation_and_viva(self):
        calc = BillCalculator(2025, 1, self.internal_fac)
        items = calc.calculate(include_amounts=True)
        lab_items = [i for i in items if i.role == 'Lab Evaluation']
        viva_items = [i for i in items if i.role == 'Lab Viva']
        self.assertEqual(len(lab_items), 1)
        self.assertEqual(lab_items[0].bill, rates.LAB_EVALUATION_RATE)
        self.assertEqual(len(viva_items), 1)
        self.assertEqual(viva_items[0].bill, 3 * rates.LAB_VIVA_PER_HOUR)

    def test_lab_invigilator(self):
        calc = BillCalculator(2025, 1, self.extra_fac)
        items = calc.calculate(include_amounts=True)
        inv_items = [i for i in items if i.role == 'Lab Invigilator']
        self.assertEqual(len(inv_items), 1)
        self.assertEqual(inv_items[0].bill, 3 * rates.LAB_INVIGILATOR_PER_HOUR)

    def test_viva_voce(self):
        calc = BillCalculator(2025, 1, self.extra_fac)
        items = calc.calculate(include_amounts=True)
        viva_items = [i for i in items if i.role == 'Viva-Voce']
        self.assertEqual(len(viva_items), 1)
        self.assertEqual(viva_items[0].bill, 2 * rates.VIVA_VOCE_PER_HOUR)

    def test_thesis_paper_evaluation(self):
        calc = BillCalculator(2025, 1, self.internal_fac)
        items = calc.calculate(include_amounts=True)
        thesis_items = [i for i in items if i.role == 'Thesis Paper Evaluation']
        self.assertEqual(len(thesis_items), 1)
        self.assertEqual(thesis_items[0].bill, 5 * rates.THESIS_PAPER_EVALUATION_PER_PAPER)

    def test_thesis_supervisor(self):
        calc = BillCalculator(2025, 1, self.internal_fac)
        items = calc.calculate(include_amounts=True)
        sup_items = [i for i in items if i.role == 'Thesis Supervisor']
        self.assertEqual(len(sup_items), 1)
        self.assertEqual(sup_items[0].bill, 3 * rates.THESIS_SUPERVISOR_PER_STUDENT)

    def test_calculate_total(self):
        calc = BillCalculator(2025, 1, self.chairman_fac)
        total = calc.calculate_total()
        items = calc.calculate(include_amounts=True)
        self.assertEqual(total, sum(i.bill for i in items))

    def test_no_amounts_mode(self):
        calc = BillCalculator(2025, 1, self.chairman_fac)
        items = calc.calculate(include_amounts=False)
        for item in items:
            self.assertEqual(item.bill, 0)

    def test_faculty_with_no_roles(self):
        no_role_fac = faculty.objects.create(
            username='norole', email='norole@test.com',
            name='Dr. NoRole', title='Lecturer', password='test123',
        )
        calc = BillCalculator(2025, 1, no_role_fac)
        items = calc.calculate(include_amounts=True)
        self.assertEqual(len(items), 0)


class GetSemesterDisplayTestCase(TestCase):
    """Tests for get_semester_display helper."""

    def test_first_year_first_semester(self):
        result = get_semester_display(1)
        self.assertIn('1st', result)

    def test_fourth_year_second_semester(self):
        result = get_semester_display(8)
        self.assertIn('4th Year', result)

    def test_masters(self):
        result = get_semester_display(9)
        self.assertIn('Masters', result)


class RatesTestCase(TestCase):
    """Tests for rates module."""

    def test_tabulation_rate_junior(self):
        self.assertEqual(rates.get_tabulation_rate(1), rates.TABULATION_RATE_JUNIOR)
        self.assertEqual(rates.get_tabulation_rate(3), rates.TABULATION_RATE_JUNIOR)

    def test_tabulation_rate_senior(self):
        self.assertEqual(rates.get_tabulation_rate(4), rates.TABULATION_RATE_SENIOR)
        self.assertEqual(rates.get_tabulation_rate(8), rates.TABULATION_RATE_SENIOR)
