from django.db import models

class Fabric(models.Model):
    name = models.CharField(max_length=64)
    SAN_VENDOR_CHOICES = [
        ('Brocade', 'Brocade'),
        ('Cisco', 'Cisco'),
    ]
    san_vendor = models.CharField(
        max_length=7,
        choices=SAN_VENDOR_CHOICES
    )
    zoneset_name = models.CharField(max_length=200)
    vsan = models.IntegerField(blank=True, null=True)
    EXIST_CHOICES = [
        ('True', 'True'),
        ('False', 'False')
    ]
    exists = models.CharField(max_length=5, choices=EXIST_CHOICES)

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
    EXIST_CHOICES = [
        ('True', 'True'),
        ('False', 'False')
    ]
    exists = models.CharField(max_length=5, choices=EXIST_CHOICES)

    def __str__(self):
        return self.alias_name
    

class Config(models.Model):
    san_vendor = models.CharField(
        max_length=7,
        choices=[
            ('BR', 'Brocade'),
            ('CI', 'Cisco'),
        ]
    )
    cisco_alias = models.CharField(
        max_length=15,
        choices=[
            ('device-alias', 'device-alias'),
            ('fcalias', 'fcalias')
        ]   
    )
    cisco_zoning_mode = models.CharField(
        max_length=15,
        choices=[
            ('basic','basic'),
            ('enhanced','enhanced')
        ]
    )
    zone_ratio = models.CharField(
        max_length=20,
        choices=[
            ('one-to-one','one-to-one'),
            ('one-to-many', 'one-to-many'),
            ('all-to-all', 'all-to-all')
        ]
    )


