from decimal import Decimal
from datetime import timedelta, datetime
from django.test import TestCase
from model_mommy import mommy
from .models import CallRecord, Bill, PriceRule
from .validators import BillValidator, BillDateValidator
from .serializers import CallRecordSerializer, BillSerializer
from .exceptions import InvalidBillDate
from pytz import UTC


class CallRecordTest(TestCase):
    def setUp(self):
        self.call_record = mommy.make(
            CallRecord, pk=10, type=1, timestamp='2018-11-25 08:08:08',
            call_id=50, source='11986091154', destination='11988888888'
        )

    def test_call_record_creation(self):
        self.assertTrue(isinstance(self.call_record, CallRecord))
        self.assertEquals(self.call_record.type, 1)
        self.assertEquals(self.call_record.call_id, 50)
        self.assertEquals(self.call_record.timestamp, '2018-11-25 08:08:08')
        self.assertEquals(self.call_record.source, '11986091154')
        self.assertEquals(self.call_record.destination, '11988888888')
        self.assertEquals(self.call_record.__str__(), '11986091154')


class BillTest(TestCase):
    def setUp(self):
        self.call_record_start_one = mommy.make(
            CallRecord, pk=1, type=1, timestamp='2018-10-31 23:55:00',
            call_id=1, source='11999998888', destination='11982223454'
        )

        self.call_record_end_one = mommy.make(
            CallRecord, pk=2, type=2, timestamp='2018-11-1 00:01:08',
            call_id=1, source='', destination=''
        )

    def test_create(self):
        bill_instance = Bill()
        bill_data_to_save = {
            'call': CallRecord.objects.get(id=2),
            'cost': 12.76,
            'call_duration': timedelta(hours=0, minutes=6, seconds=8),
            'call_start': datetime(2018, 10, 31, 23, 55, 00, tzinfo=UTC),
            'call_end': datetime(2018, 11, 1, 00, 1, 8, tzinfo=UTC),
            'month': 11,
            'year': 2018
        }

        bill_instance.create(bill_data=bill_data_to_save)


class PriceRuleTest(TestCase):
    def setUp(self):
        self.price_rule = mommy.make(
            PriceRule, rule_type=1, fixed_charge=Decimal('0.36'),
            call_charge=Decimal('0.09'),
            start_period=datetime(2018, 7, 10, 22, 0, 0).time(),
            end_period=datetime(2018, 7, 10, 6, 0, 0).time()
        )

    def test_price_rule_create(self):
        price_rule_one = PriceRule.objects.get(id=1)

        self.assertEqual(
            self.price_rule.rule_type,
            price_rule_one.rule_type
        )
        self.assertEqual(
            self.price_rule.fixed_charge,
            price_rule_one.fixed_charge
        )
        self.assertEqual(
            self.price_rule.call_charge,
            price_rule_one.call_charge
        )
        self.assertEqual(
            self.price_rule.start_period,
            price_rule_one.start_period
        )
        self.assertEqual(
            self.price_rule.end_period,
            price_rule_one.end_period
        )


class CallRecordSerializerTest(TestCase):
    def setUp(self):
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
            'timestamp': datetime(2018, 7, 22, 7, 0, 56, tzinfo=UTC)
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
            CallRecord, pk=1, type=2, timestamp='2018-11-25 09:08:08',
            call_id=1, source='', destination=''
        )

        self.call_record_start_one = mommy.make(
            CallRecord, pk=2, type=1, timestamp='2018-11-25 08:08:08',
            call_id=1, source='11999998888', destination='11982223454'
        )

        self.bill_attributes = {
            'call_record': CallRecord.objects.get(id=2),
            'call_cost': 12.76,
            'call_duration': str(timedelta(hours=1)),
            'fk_call_end': str(datetime(2018, 11, 25, 9, 8, 8, tzinfo=UTC)),
            'fk_call_start': str(datetime(2018, 11, 25, 8, 8, 8, tzinfo=UTC)),
            'month': 11,
            'year': 2018
        }

        self.serializer_data = {
            'call_record': CallRecord.objects.get(id=2),
            'cost': 12.76,
            'call_duration': "01:00:00",
            'call_end': "2018-11-25T09:08:08Z",
            'call_start': "2018-11-25T08:08:08Z",
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
                'destination', 'id', 'call_duration',
                'call_cost', 'fk_call_start', 'fk_call_end'
                ])
        )


class BillValidatorTest(TestCase):
    def setUp(self):
        self.call_record_end_one = mommy.make(
            CallRecord, pk=1, type=2, timestamp='2018-11-25 09:08:08',
            call_id=1, source='', destination=''
        )

        self.call_record_start_one = mommy.make(
            CallRecord, pk=2, type=1, timestamp='2018-11-25 08:08:08',
            call_id=1, source='11999998888', destination='11982223454'
        )

        self.call_record_start_two = mommy.make(
            CallRecord, pk=3, type=2, timestamp='2018-11-25 08:08:08',
            call_id=2, source='', destination=''
        )

    def test_existent_start_type_true(self):
        validator_instance = BillValidator()
        call_id = CallRecord.objects.get(id=1).call_id

        actual = validator_instance._BillValidator__existent_pair_record(
            call_id
        )

        self.assertTrue(actual)

    def test_existent_start_type_false(self):
        validator_instance = BillValidator()

        call_id = CallRecord.objects.get(id=3).call_id

        actual = validator_instance._BillValidator__existent_pair_record(
            call_id
        )

        self.assertFalse(actual)

    def test_validate_bill_to_record_true(self):
        validator_instance = BillValidator()
        call_record_serializer = CallRecordSerializer(
            CallRecord.objects.get(id=1), many=False
        )

        actual = validator_instance.validate_bill_to_record(
            call_data=call_record_serializer.data
        )

        self.assertTrue(actual)

    def test_validate_bill_to_record_false(self):
        validator_instance = BillValidator()
        call_record_serializer = CallRecordSerializer(
            CallRecord.objects.get(id=3), many=False
        )

        actual = validator_instance.validate_bill_to_record(
            call_data=call_record_serializer.data
        )

        self.assertFalse(actual)

    def test_validate_bill_to_record_type_start_false(self):
        validator_instance = BillValidator()
        call_record_serializer = CallRecordSerializer(
            CallRecord.objects.get(id=2), many=False
        )

        actual = validator_instance.validate_bill_to_record(
            call_data=call_record_serializer.data
        )

        self.assertFalse(actual)

    def test_prepare_bill_data(self):
        validator_instance = BillValidator()
        call_record_serializer = {
            'type': 2,
            'timestamp': datetime(2018, 11, 25, 9, 8, 8, tzinfo=UTC),
            'call_id': 1
        }

        actual = validator_instance.prepare_bill_data(
            call_record_data=call_record_serializer
        )

        expected = {
            'call': CallRecord.objects.get(id=2),
            'cost': 12.76,
            'call_duration': timedelta(hours=1),
            'call_end': datetime(2018, 11, 25, 9, 8, 8, tzinfo=UTC),
            'call_start': datetime(2018, 11, 25, 8, 8, 8, tzinfo=UTC),
            'month': 11,
            'year': 2018
        }

        self.assertEquals(actual, expected)


class BillDateValidatorTest(TestCase):
    def test_validate_bill_date(self):
        bill_date_validator = BillDateValidator()
        actual = bill_date_validator.validate_bill_date('5', '2017')
        bill_date_validator.actual_date = datetime(2018, 5, 25)

        expected = {
            "month": 5,
            "year": 2017
        }

        self.assertEqual(actual, expected)

    def test_validate_bill_date_raises(self):
        bill_date_validator = BillDateValidator()
        bill_date_validator.actual_date = datetime(2018, 5, 25)

        with self.assertRaises(InvalidBillDate):
            bill_date_validator.validate_bill_date('5', '12017')

        with self.assertRaises(InvalidBillDate):
            bill_date_validator.validate_bill_date('13', '2017')

        with self.assertRaises(InvalidBillDate):
            bill_date_validator.validate_bill_date('5', '2018')

        with self.assertRaises(InvalidBillDate):
            bill_date_validator.validate_bill_date('1', '2019')

    def test_validate_bill_date_date_none(self):
        bill_date_validator = BillDateValidator()
        bill_date_validator.actual_date = datetime(2018, 5, 25)
        actual = bill_date_validator.validate_bill_date()

        expected = {
            "month": 4,
            "year": 2018
        }

        self.assertEqual(actual, expected)
