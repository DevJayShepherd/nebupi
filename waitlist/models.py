from django.db import models


class WaitlistEntry(models.Model):
    email = models.EmailField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0, help_text="Position in the waitlist")

    class Meta:
        ordering = ['position', 'timestamp']

    def __str__(self):
        return f"{self.email} - Position: {self.position}"
