"""Course code master model — predefined course codes managed by chairman."""

from django.db import models
from django.contrib.auth.models import User


class CourseCodeMaster(models.Model):
    """Predefined course code with default name. Chairman/superuser managed."""
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'root'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"
