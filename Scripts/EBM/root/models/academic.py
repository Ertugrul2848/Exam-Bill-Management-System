"""Academic session and semester models."""

from django.db import models
from django.core.validators import MinValueValidator
from .faculty import faculty, External


class Session(models.Model):
    """Academic session (year)."""
    year = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(1900)],
    )

    class Meta:
        app_label = 'root'

    def __str__(self):
        return str(self.year)


class Semester(models.Model):
    """Semester within an academic session, including its exam committee."""
    SEMESTER_CHOICES = [
        (1, "1st Year 1st Semester"),
        (2, "1st Year 2nd Semester"),
        (3, "2nd Year 1st Semester"),
        (4, "2nd Year 2nd Semester"),
        (5, "3rd Year 1st Semester"),
        (6, "3rd Year 2nd Semester"),
        (7, "4th Year 1st Semester"),
        (8, "4th Year 2nd Semester"),
        (9, "Masters 1st Semester"),
        (10, "Masters 2nd Semester"),
    ]
    semId = models.IntegerField(choices=SEMESTER_CHOICES)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    chairman = models.OneToOneField(
        faculty, related_name='chairman', on_delete=models.CASCADE)
    tabular1 = models.ForeignKey(
        faculty, related_name="tabular1", on_delete=models.CASCADE)
    tabular2 = models.ForeignKey(
        faculty, related_name="tabular2", on_delete=models.CASCADE)
    external = models.ForeignKey(External, on_delete=models.CASCADE)
    acting_chairman = models.ForeignKey(
        faculty, related_name='acting_chairman', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    is_archived = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    class Meta:
        app_label = 'root'
        unique_together = [('session', 'semId')]

    def get_display_name(self):
        """Return human-readable semester name."""
        return self.get_semId_display()

    def __str__(self):
        return str(str(self.session) + " " + str(self.semId))
