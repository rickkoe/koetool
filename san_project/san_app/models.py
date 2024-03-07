from django.db import models
from django.core.exceptions import ValidationError


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


class Storage(models.Model):
    name = models.CharField(max_length=64)
    customer = models.ForeignKey(Customer, related_name='storage_customer',
                    on_delete=models.CASCADE) 
    storage_type = models.CharField(max_length=20, choices=[('FlashSystem', 'FlashSystem'), ('DS8000', 'DS8000')])
    location = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f'{self.customer}: {self.name}' 
    
    class Meta:
        unique_together = ['customer', 'name']

class Alias(models.Model):
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='alias_storage', null=True, blank=True)
    USE_CHOICES = [
        ('init', 'Initiator'),
        ('target', 'Target'),
        ('both', 'Both'),
    ]
    name = models.CharField(max_length=100, unique=False)
    wwpn = models.CharField(max_length=23)
    use = models.CharField(max_length=6, choices=USE_CHOICES, null=True, blank=True)
    create = models.BooleanField(default=False)
    include_in_zoning = models.BooleanField(default=False)

    @property
    def customer(self):
        return self.fabric.customer if self.fabric else None
    
    class Meta:
        ordering = ['name']
        unique_together = ['fabric', 'wwpn']
    
    def __str__(self):
        return f'{self.fabric.customer}: {self.name}'


class ZoneGroup(models.Model):
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=False)
    create = models.BooleanField(default=False)
    aliases = models.ManyToManyField(Alias)
    zone_type = models.CharField(max_length=100,choices=[
        ('smart', 'smart'),
        ('standard', 'standard'),
    ])
    exists = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.fabric.customer}: {self.name}'


class Zone(models.Model):
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=False)
    create = models.BooleanField(default=False)
    exists = models.BooleanField(default=False)
    zone_type = models.CharField(max_length=100,choices=[
        ('smart', 'smart'),
        ('standard', 'standard'),
    ])
    members = models.ManyToManyField(Alias)

    @property
    def customer(self):
        return self.fabric.customer

    def __str__(self):
        return f'{self.fabric.customer}: {self.name}'
    
    def clean(self):
        # Check if there is any other Zone with the same name for the same customer
        if Zone.objects.filter(name=self.name, fabric__customer=self.customer).exists():
            raise ValidationError('Zone with this name already exists for this customer.')

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
    zoning_job_name = models.CharField(max_length=40)
    smartzone_prefix = models.CharField(max_length=25)
    alias_max_zones = models.IntegerField()