from rest_framework import serializers
from .models import CallRecord, Bill, PriceRule
from .validators import BillValidator


class CallRecordSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        call_record_instance = super(CallRecordSerializer, self)\
            .create(validated_data)

        bill_validator = BillValidator()
        if bill_validator.validate_bill_to_record(call_data=validated_data):
            bill_member = Bill()
            bill_member.create(
                bill_data=bill_validator.prepare_bill_data(validated_data))

        return call_record_instance

    class Meta:
        model = CallRecord
        fields = '__all__'
        extra_kwargs = {
            'source': {'allow_blank': True},
            'destination': {'allow_blank': True}
        }


class BillSerializer(serializers.ModelSerializer):
    destination = serializers.SerializerMethodField('get_call_record')

    class Meta:
        exclude = ('month', 'year', 'call_record')
        model = Bill

    def get_call_record(self, object):
        return object.call_record.destination


class PriceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = PriceRule
