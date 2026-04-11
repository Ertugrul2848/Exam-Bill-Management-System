"""Billing URL patterns."""

from django.urls import path
from ..views import examBill, indBill, pdf_view, examBill2, semBill, indBill2, all_bills

urlpatterns = [
    path('examBill/', examBill, name='examBill'),
    path('indBill/<int:id>/<int:id2>/<int:id3>/', indBill, name='indBill'),
    path('pdf_view/<int:id>/<int:id2>/<int:id3>/', pdf_view, name="pdf_view"),
    path('examBill2/', examBill2, name='examBill2'),
    path('semBill/<int:id>/<int:id2>/', semBill, name='semBill'),
    path('indBill2/<int:id>/<int:id2>/<int:id3>/', indBill2, name='indBill2'),
    path('all-bills/', all_bills, name='all_bills'),
]
