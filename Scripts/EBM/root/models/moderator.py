"""ModeratorRole model — configurable moderator permissions at system or semester level."""

from django.db import models
from django.contrib.auth.models import User
from .faculty import faculty
from .academic import Session, Semester


class ModeratorRole(models.Model):
    SCOPE_CHOICES = [('system', 'System'), ('semester', 'Semester')]

    user = models.ForeignKey(faculty, on_delete=models.CASCADE, related_name='moderator_roles')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    can_create_semester = models.BooleanField(default=False)
    can_view_semester_bill = models.BooleanField(default=False)
    can_view_all_bills = models.BooleanField(default=False)
    can_view_session_bills = models.BooleanField(default=False)
    can_approve_requests = models.BooleanField(default=False)
    view_only = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'root'
        unique_together = ['user', 'semester']

    def __str__(self):
        return f"{self.user.name} \u2014 {self.scope} moderator"
