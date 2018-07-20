from decimal import Decimal
from datetime import timedelta, datetime
from model_mommy import mommy
from django.test import TestCase
from callcenter.models import CallRecord, Bill, PriceRule


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
            CallRecord, pk=2, type=2, timestamp='2018-11-2 00:01:08',
            call_id=1, source='', destination=''
        )

    def test_create(self):
        bill_instance = Bill()
        bill_data_to_save = {
            'call': CallRecord.objects.get(id=2),
            'cost': 12.76,
            'call_duration': timedelta(hours=24, minutes=6, seconds=8),
            'call_start': datetime(2018, 10, 31, 23, 55, 00),
            'call_end': datetime(2018, 11, 2, 00, 1, 8),
            'month': 11,
            'year': 2018
        }

        bill_instance.create(bill_data=bill_data_to_save)

    def test_call_record_creation_exception(self):
        bill_instance = Bill()
        bill_data_to_save = {
            'call': CallRecord.objects.get(id=2),
            'cost': 12.76,
            'call_duration': timedelta(hours=24, minutes=6, seconds=8),
            'call_start': datetime(2018, 10, 31, 23, 55, 00),
            'call_end': timedelta(hours=10),
            'month': 11,
            'year': 2018
        }

        expected = (
            '["\'10:00:00\' value has an invalid format. It must '
            'be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format."]'
        )

        actual = bill_instance.create(bill_data=bill_data_to_save)

        self.assertEqual(actual, expected)


class PriceRuleTest(TestCase):
    def setUp(self):
        self.price_rule = mommy.make(
            PriceRule, pk=1, rule_type=1, fixed_charge=Decimal('0.36'),
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
