from rest_framework import serializers
from .models import SANAlias

class SANAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = SANAlias
        fields = '__all__'
