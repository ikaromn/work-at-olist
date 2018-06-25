from rest_framework import serializers
from .models import CallRecord


class CallRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallRecord
        fields = '__all__'
        extra_kwargs = {
            'source': {'allow_blank': True},
            'destination': {'allow_blank': True}
        }
