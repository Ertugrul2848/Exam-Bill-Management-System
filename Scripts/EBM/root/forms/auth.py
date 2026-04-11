"""Authentication forms."""

from django import forms


class LoginForm(forms.Form):
    """Login form for faculty members."""
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
