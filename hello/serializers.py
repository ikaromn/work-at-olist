from rest_framework import serializers
from .models import CallRecord

class CallRecordSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        #import pdb;pdb.set_trace()
        try:
            CallRecord.objects.get(type=validated_data['type'], call_id=validated_data['call_id'])
        except CallRecord.DoesNotExist:
            return CallRecord.objects.create(**validated_data)
        
        raise serializers.ValidationError('This call type ready exist with the call_id %s' % validated_data['call_id'])

    class Meta:
        model = CallRecord
        fields = '__all__'
        extra_kwargs = {
            'source': {'allow_blank': True},
            'destination': {'allow_blank': True}
        }