from datetime import datetime
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
    start = serializers.SerializerMethodField('get_fk_call_start')
    end = serializers.SerializerMethodField('get_fk_call_end')
    duration = serializers.SerializerMethodField()

    class Meta:
        exclude = (
            'month', 'year', 'call_record',
            'id', 'fk_call_start', 'fk_call_end'
        )
        model = Bill

    def get_call_record(self, object):
        return object.call_record.destination

    def get_fk_call_start(self, object):
        return object.fk_call_start

    def get_fk_call_end(self, object):
        return object.fk_call_end

    def get_duration(self, object):
        time_diff = object.fk_call_end - object.fk_call_start

        return self._convert_time(time_diff)

    def _convert_time(self, time):
        days, seconds = time.days, time.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)

        return "%02dh%02dm%02ds" % (hours, minutes, seconds)


class PriceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = PriceRule
