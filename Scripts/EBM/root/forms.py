"""
Django forms for the Exam Bill Management System.

This module provides form classes for user input validation:
- LoginForm: Handles faculty login via email/password.
- CommitteeCreateForm: Handles exam committee creation with validation
  to prevent duplicate faculty assignments.

Note: LoginForm is not yet integrated into the login view (views.log still
uses raw POST data). Integration is planned for a future ticket.
"""

from django import forms
from .models import faculty, External, Session, Semester


class LoginForm(forms.Form):
    """
    Login form for faculty members.

    Uses email + password authentication (matching the faculty model's
    plaintext password field). This form validates input format only —
    actual authentication is handled by the view via Django's authenticate().

    Fields:
        email: Faculty email address (used to look up the faculty record).
        password: Plaintext password (matched against faculty.password).
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'a@gmail.com',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '*******',
            'class': 'form-control',
        })
    )


class CommitteeCreateForm(forms.Form):
    """
    Form for creating a new exam committee (semester).

    Creates a Semester record with assigned committee members. Validates that:
    - No faculty member is assigned to more than one role (chairman/tabular1/tabular2).
    - All required fields are provided.

    Querysets for faculty/external fields are refreshed in __init__ to avoid
    stale data from module-level evaluation.

    Fields:
        session: Academic session (year) — validated against existing Session records.
        semester: Semester ID (1-10) from SEMESTER_CHOICES.
        chairman: Faculty member to chair the committee.
        tabular1: First tabulator faculty member.
        tabular2: Second tabulator faculty member.
        external: External examiner from the External model.
    """
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Session',
        empty_label='---',
    )
    semester = forms.ChoiceField(
        choices=[('', '---')] + Semester.SEMESTER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Semester',
    )
    chairman = forms.ModelChoiceField(
        queryset=faculty.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Chairman',
        to_field_name='email',
        empty_label='---',
    )
    tabular1 = forms.ModelChoiceField(
        queryset=faculty.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Tabular1',
        to_field_name='email',
        empty_label='---',
    )
    tabular2 = forms.ModelChoiceField(
        queryset=faculty.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Tabular2',
        to_field_name='email',
        empty_label='---',
    )
    external = forms.ModelChoiceField(
        queryset=External.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select External',
        to_field_name='email',
        empty_label='---',
    )

    def __init__(self, *args, **kwargs):
        """Refresh querysets to include newly added faculty/external members."""
        super().__init__(*args, **kwargs)
        self.fields['chairman'].queryset = faculty.objects.all()
        self.fields['tabular1'].queryset = faculty.objects.all()
        self.fields['tabular2'].queryset = faculty.objects.all()
        self.fields['external'].queryset = External.objects.all()

    def clean(self):
        """Validate that no faculty member is assigned to multiple committee roles."""
        cleaned_data = super().clean()
        chairman = cleaned_data.get('chairman')
        tabular1 = cleaned_data.get('tabular1')
        tabular2 = cleaned_data.get('tabular2')

        if chairman and tabular1 and tabular2:
            if tabular1 == tabular2 or tabular1 == chairman or tabular2 == chairman:
                raise forms.ValidationError(
                    'Faculty can not be selected more than once !!'
                )

        return cleaned_data
