from decimal import Decimal
from datetime import timedelta, datetime
from model_mommy import mommy
from django.test import TestCase
from callcenter.models import CallRecord, Bill, PriceRule
from callcenter.serializers import CallRecordSerializer, BillSerializer


class CallRecordSerializerTest(TestCase):
    def setUp(self):
        self.price_rule_standart = mommy.make(
            PriceRule, id=1, rule_type=1, fixed_charge=Decimal('0.36'),
            call_charge=Decimal('0.09'),
            start_period=datetime(2018, 7, 10, 6, 0, 0).time(),
            end_period=datetime(2018, 7, 10, 22, 0, 0).time()
        )

        self.price_rule_reduced = mommy.make(
            PriceRule, id=2, rule_type=2, fixed_charge=Decimal('0.36'),
            call_charge=Decimal('0'),
            start_period=datetime(2018, 7, 9, 22, 0, 0).time(),
            end_period=datetime(2018, 7, 10, 6, 0, 0).time()
        )

        self.call_record_attributes_start = {
            'type': 1,
            'call_id': 1,
            'source': '11986091154',
            'destination': '11982223465',
            'timestamp': datetime(2018, 7, 22, 6, 0, 56)
        }

        self.call_record_attributes_end = {
            'type': 2,
            'call_id': 1,
            'timestamp': datetime(2018, 7, 22, 7, 0, 56)
        }

        self.serializer_data = {
            'type': 1,
            'call_id': 1,
            'source': '11986091154',
            'destination': '11982223465',
            'timestamp': '2018-7-22 06:00:56'
        }

    def test_serializer_create(self):
        call_record_serializer_instance_one = CallRecordSerializer()
        call_record_serializer_instance_two = CallRecordSerializer()

        self.serializer_one = call_record_serializer_instance_one.create(
            validated_data=self.call_record_attributes_start
        )

        self.serializer_two = call_record_serializer_instance_two.create(
            validated_data=self.call_record_attributes_end
        )

        self.assertIsInstance(self.serializer_one, CallRecord)
        self.assertIsInstance(self.serializer_two, CallRecord)


class BillSerializerTest(TestCase):
    def setUp(self):
        self.call_record_end_one = mommy.make(
            CallRecord, pk=1, type=2, timestamp='2018-11-27 09:08:08',
            call_id=1, source='', destination=''
        )

        self.call_record_start_one = mommy.make(
            CallRecord, pk=2, type=1, timestamp='2018-11-25 08:08:08',
            call_id=1, source='11999998888', destination='11982223454'
        )

        self.bill_attributes = {
            'call_record': CallRecord.objects.get(id=2),
            'call_cost': 12.76,
            'fk_call_end': datetime(2018, 11, 27, 9, 8, 8),
            'fk_call_start': datetime(2018, 11, 25, 8, 8, 8),
            'month': 11,
            'year': 2018
        }

        self.serializer_data = {
            'call_record': CallRecord.objects.get(id=2),
            'cost': 12.76,
            'fk_call_end': "2018-11-27T09:08:08Z",
            'fk_call_start': "2018-11-25T08:08:08Z",
            'month': 11,
            'year': 2018
        }

        self.bill = Bill.objects.create(**self.bill_attributes)
        self.serializer = BillSerializer(instance=self.bill)

    def test_serializer_create(self):
        data = self.serializer.data

        self.assertEqual(
            set(data.keys()),
            set([
                'destination', 'duration',
                'call_cost', 'start', 'end'
                ])
        )
