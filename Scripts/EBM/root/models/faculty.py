"""Faculty and External examiner models."""

from django.db import models


class faculty(models.Model):
    """Faculty member (teacher/instructor) profile."""
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=15, blank=True)
    is_profile_complete = models.BooleanField(default=True)

    class Meta:
        app_label = 'root'

    def __str__(self):
        return str(self.email)


class External(models.Model):
    """External examiner profile."""
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()

    class Meta:
        app_label = 'root'

    def __str__(self):
        return self.name
