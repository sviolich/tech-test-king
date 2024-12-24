from rest_framework import serializers
from .models import PackageEvent

class PackageEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageEvent
        fields = ['timestamp', 'package', 'event_type']
