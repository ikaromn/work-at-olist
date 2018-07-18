from decimal import Decimal
from datetime import timedelta, datetime
from model_mommy import mommy
from django.test import TestCase
from callcenter.models import CallRecord, Bill, PriceRule
from callcenter.validators import (
    BillValidator, BillDateValidator, PriceGenerator)
from callcenter.serializers import CallRecordSerializer, BillSerializer
from callcenter.exceptions import InvalidBillDate


class BillValidatorTest(TestCase):
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

    def test_prepare_bill_data(self):
        validator_instance = BillValidator()
        call_record_serializer = {
            'type': 2,
            'timestamp': datetime(2018, 11, 25, 9, 8, 8),
            'call_id': 1
        }

        actual = validator_instance.prepare_bill_data(
            call_record_data=call_record_serializer
        )

        expected = {
            'call': CallRecord.objects.get(id=2),
            'cost': Decimal('5.76'),
            'call_end': datetime(2018, 11, 25, 9, 8, 8),
            'call_start': datetime(2018, 11, 25, 8, 8, 8),
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


class PriceGeneratorTest(TestCase):
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

        self.call_record_end_one = mommy.make(
            CallRecord, pk=1, type=2, timestamp='2018-11-25 22:10:56',
            call_id=1, source='', destination=''
        )

        self.call_record_start_one = mommy.make(
            CallRecord, pk=2, type=1, timestamp='2018-11-25 21:57:13',
            call_id=1, source='11999998888', destination='11982223454'
        )

    def test_generate_cost(self):
        period_validator_instance = PriceGenerator()
        actual = period_validator_instance.generate_cost(1)
        self.assertEqual(actual, Decimal('0.54'))
