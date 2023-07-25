from django import forms
from .models import Config

class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = ['customer', 'san_vendor', 'cisco_alias', 'cisco_zoning_mode', 'zone_ratio', 'smartzone_prefix']
