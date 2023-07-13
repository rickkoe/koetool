from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.SANAlias)
admin.site.register(models.Fabric)
admin.site.register(models.Config)
admin.site.register(models.Volume)
admin.site.register(models.Zone)