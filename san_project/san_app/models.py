from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    

class Fabric(models.Model):
    customer = models.ForeignKey(Customer, related_name='fabric_customer',
                        on_delete=models.CASCADE)    
    name = models.CharField(max_length=64)
    zoneset_name = models.CharField(max_length=200)
    vsan = models.IntegerField(blank=True, null=True)
    exists = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.customer}: {self.name}'
    
    class Meta:
        unique_together = ['customer', 'name']


class Alias(models.Model):
    customer = models.ForeignKey(Customer, related_name='alias_customer',
                        on_delete=models.CASCADE)
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE,blank=True, null=True)
    USE_CHOICES = [
        ('init', 'Initiator'),
        ('target', 'Target'),
        ('both', 'Both'),
    ]
    name = models.CharField(max_length=100, unique=False)
    wwpn = models.CharField(max_length=23, unique=True)
    use = models.CharField(max_length=6, choices=USE_CHOICES, null=True, blank=True)
    create = models.BooleanField(default=False)
    include_in_zoning = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.customer}: {self.name}'

class Zone(models.Model):
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE,blank=True, null=True)
    name = models.CharField(max_length=100, unique=False)
    create = models.BooleanField(default=False)
    zone_type = models.CharField(max_length=100,choices=[
        ('smart', 'smart'),
        ('standard', 'standard'),
    ])
    exists = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.fabric.customer}: {self.name}'
    


class Config(models.Model):
    customer = models.ForeignKey(Customer, related_name='active_customer',
                        on_delete=models.CASCADE)
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