from django.db import models

class SANAlias(models.Model):
    USE_CHOICES = [
        ('init', 'Initiator'),
        ('target', 'Target'),
        ('both', 'Both'),
    ]
    
    alias_name = models.CharField(max_length=100, unique=True)
    WWPN = models.CharField(max_length=23, unique=True)
    use = models.CharField(max_length=6, choices=USE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.alias_name
