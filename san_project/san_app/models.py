from django.db import models
from django.core.exceptions import ValidationError


class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    

class Project(models.Model):
    customer = models.ForeignKey(Customer, related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['customer', 'name']
    
    class Meta:
        unique_together = ['customer', 'name']

    def __str__(self):
        return f'{self.customer}: {self.name}'


class Fabric(models.Model):
    project = models.ForeignKey(Project, related_name='fabrics', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    zoneset_name = models.CharField(max_length=200)
    vsan = models.IntegerField(blank=True, null=True)
    exists = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.project}: {self.name}'
    
    class Meta:
        unique_together = ['project', 'name']


class Storage(models.Model):
    project = models.ForeignKey(Project, related_name='storages', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    storage_type = models.CharField(
        max_length=20,
        choices=[
            ('FlashSystem', 'FlashSystem'), 
            ('DS8000', 'DS8000'),
            ('Switch', 'Switch'),
            ('Data Domain', 'Data Domain')
            ])
    location = models.CharField(max_length=100, blank=True, null=True)
    machine_type = models.CharField(max_length=4, blank=True, null=True)
    model = models.CharField(max_length=3, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    system_id = models.CharField(max_length=16, blank=True, null=True)
    wwnn = models.CharField(max_length=23, blank=True, null=True)
    firmware_level = models.CharField(max_length=16, blank=True, null=True)
    primary_ip = models.CharField(max_length=11, blank=True, null=True)
    secondary_ip = models.CharField(max_length=11, blank=True, null=True)

    def storage_image(self):
        storage_image = f'IBM.2107-{self.serial_number[:-1] + "1"}'
        return storage_image
    
    def __str__(self):
        return f'{self.project}: {self.name}' 
    
    class Meta:
        unique_together = ['project', 'name']

class Host(models.Model):
    project = models.ForeignKey(Project, related_name='host_project', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    storage = models.ForeignKey(Storage, related_name="owning_storage", on_delete=models.CASCADE, null=True,blank=True)

    class Meta:
        unique_together = ['project', 'name']

    def __str__(self):
        return f'{self.project}: {self.name}'
    
class Alias(models.Model):
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='aliases', null=True, blank=True)
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
    host = models.ForeignKey(Host, on_delete=models.SET_NULL, related_name='alias_host', null=True, blank=True)

    @property
    def project(self):
        return self.fabric.project if self.fabric else None
    
    class Meta:
        ordering = ['name']
        unique_together = [
            ('fabric', 'wwpn'),
            ('fabric', 'name'),
        ]
    
    def __str__(self):
        return f'{self.fabric.project}: {self.name}'


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
        return f'{self.fabric.project}: {self.name}'


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
    def project(self):
        return self.fabric.project

    def __str__(self):
        return f'{self.fabric.project}: {self.name}'
    
    def clean(self):
        # Check if there is any other Zone with the same name for the same project
        if Zone.objects.filter(name=self.name, fabric__project=self.project).exists():
            raise ValidationError('Zone with this name already exists for this project.')

class Config(models.Model):
    project = models.ForeignKey(Project, related_name='configs', on_delete=models.CASCADE)
    san_vendor = models.CharField(
        max_length=7,
        choices=[
            ('BR', 'Brocade'),
            ('CI', 'Cisco'),
        ],
        default='BR'
    )
    cisco_alias = models.CharField(
        max_length=15,
        choices=[
            ('device-alias', 'device-alias'),
            ('fcalias', 'fcalias'),
            ('wwpn', 'wwpn')
        ],
        default='device-alias'  
    )
    cisco_zoning_mode = models.CharField(
        max_length=15,
        choices=[
            ('basic','basic'),
            ('enhanced','enhanced')
        ],
        default='enhanced'
    )
    zone_ratio = models.CharField(
        max_length=20,
        choices=[
            ('one-to-one','one-to-one'),
            ('one-to-many', 'one-to-many'),
            ('all-to-all', 'all-to-all')
        ],
        default='one-to-one'
    )
    zoning_job_name = models.CharField(max_length=40, default='default_job')
    smartzone_prefix = models.CharField(max_length=25, default='')
    alias_max_zones = models.IntegerField(default=1)


class VolumeRange(models.Model):
    project = models.ForeignKey(Project, related_name='volume_ranges', on_delete=models.CASCADE)
    site = models.CharField(max_length=200, null=True, blank=True)
    lpar = models.CharField(max_length=200, null=True, blank=True)
    use = models.CharField(max_length=200, null=True, blank=True)
    source_ds8k = models.ForeignKey(Storage, related_name='ds_source', on_delete=models.CASCADE, null=True, blank=True)
    source_pool = models.CharField(max_length=100)
    source_start = models.CharField(max_length=4)
    source_end = models.CharField(max_length=4)
    target_ds8k = models.ForeignKey(Storage, related_name='ds_target', on_delete=models.CASCADE, null=True, blank=True)
    target_start = models.CharField(max_length=4)
    target_end = models.CharField(max_length=4)
    # voltype = models.CharField(
    #     max_length=3,
    #             choices=[
    #         ('CKD','CKD'),
    #         ('FB', 'FB'),
    #     ],
    #     default='CKD'
    # )
    create = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.project}: {self.source_start}-{self.source_end}'

