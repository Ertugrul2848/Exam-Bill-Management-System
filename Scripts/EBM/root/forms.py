from django import forms
from .models import faculty, External, Semester


class LoginForm(forms.Form):
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
    session = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
        }),
        label='Select Session',
    )
    semester = forms.ChoiceField(
        choices=[('', '---')] + Semester.SEMESTER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Semester',
    )
    chairman = forms.ModelChoiceField(
        queryset=faculty.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Chairman',
        to_field_name='email',
        empty_label='---',
    )
    tabular1 = forms.ModelChoiceField(
        queryset=faculty.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Tabular1',
        to_field_name='email',
        empty_label='---',
    )
    tabular2 = forms.ModelChoiceField(
        queryset=faculty.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Tabular2',
        to_field_name='email',
        empty_label='---',
    )
    external = forms.ModelChoiceField(
        queryset=External.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select External',
        to_field_name='email',
        empty_label='---',
    )

    def clean(self):
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
