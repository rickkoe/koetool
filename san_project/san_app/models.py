from django.db import models

class Fabric(models.Model):
    name = models.CharField(max_length=64)
    SAN_VENDOR_CHOICES = [
        ('BR', 'Brocade'),
        ('CI', 'Cisco'),
    ]
    san_vendor = models.CharField(
        max_length=2,
        choices=SAN_VENDOR_CHOICES
    )
    zoneset_name = models.CharField(max_length=200)
    vsan = models.IntegerField(blank=True, null=True)
    # exists = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SANAlias(models.Model):
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE, null=True)
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
