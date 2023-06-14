from django import forms
from django.core.exceptions import ValidationError
import re
from .models import SANAlias

def validate_wwpn(value):
    # WWPN should consist of 16 hexadecimal characters or 8 pairs of hexadecimal characters separated by colons
    regex_no_colon = r'^[0-9a-fA-F]{16}$'
    regex_with_colon = r'^([0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$'
    if not re.match(regex_no_colon, value) and not re.match(regex_with_colon, value):
        raise ValidationError('Invalid WWPN format - WWPN should consist of 16 hexadecimal characters or 8 pairs of hexadecimal characters separated by colons')

class SANAliasForm(forms.ModelForm):
    use = forms.ChoiceField(choices=SANAlias.USE_CHOICES)

    class Meta:
        model = SANAlias
        fields = ['alias_name', 'WWPN', 'use']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['WWPN'].validators.append(validate_wwpn)

    def clean_WWPN(self):
        wwpn = self.cleaned_data.get('WWPN')

        # If the WWPN is in a valid format but doesn't include colons, add them
        if re.match(r'^[0-9a-fA-F]{16}$', wwpn):
            wwpn = ':'.join(wwpn[i:i+2] for i in range(0, len(wwpn), 2))

        return wwpn
