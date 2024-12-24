from django.db import models

class PackageEvent(models.Model):
    timestamp = models.DateTimeField()
    package = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50)  # e.g., 'install', 'uninstall'

    def __str__(self):
        return f"{self.event_type.capitalize()} - {self.package} at {self.timestamp}"
