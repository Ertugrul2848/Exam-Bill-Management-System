"""Teacher registration request model."""

from django.db import models


class RegistrationRequest(models.Model):
    """Pending teacher registration awaiting chairman approval."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'root'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email}) — {self.status}"
