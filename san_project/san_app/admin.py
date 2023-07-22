from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Customer)
admin.site.register(models.Alias)
admin.site.register(models.Fabric)
admin.site.register(models.Config)
admin.site.register(models.ZoneGroup)
admin.site.register(models.Storage)
