import json
from decimal import Decimal
from datetime import datetime
from django.test import TestCase, RequestFactory
from model_mommy import mommy
from rest_framework import status
from callcenter.views import BillByMonth
from callcenter.models import CallRecord, Bill, PriceRule
from callcenter.serializers import CallRecordSerializer, BillSerializer


class IndexTest(TestCase):
    def test_post_call_record_start(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CallRecordApiPostTest(TestCase):
    def setUp(self):
        price_rule_stand = {
            'rule_type': 1,
            'fixed_charge': 0.36,
            'call_charge': 0.09,
            'start_period': '06:00:00',
            'end_period': '22:00:00'
        }

        price_rule_reduced = {
            'rule_type': 2,
            'fixed_charge': 0.36,
            'call_charge': 0.0,
            'start_period': '22:00:00',
            'end_period': '06:00:00'
        }
        self.client.post('/price-rules/', format='json', data=price_rule_stand)
        self.client.post(
            '/price-rules/', format='json', data=price_rule_reduced
        )

    def test_post_call_record_start(self):
        call_record_start = {
            'type': 1,
            'timestamp': '2018-6-15 05:22:00',
            'call_id': 1,
            'source': '11986091154',
            'destination': '11982220546'
        }

        response = self.client.post(
            '/call-records/', format='json', data=call_record_start
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BillByMonthGetTest(TestCase):
    def setUp(self):
        price_rule_stand = {
            'rule_type': 1,
            'fixed_charge': 0.36,
            'call_charge': 0.09,
            'start_period': '06:00:00',
            'end_period': '22:00:00'
        }

        price_rule_reduced = {
            'rule_type': 2,
            'fixed_charge': 0.36,
            'call_charge': 0.0,
            'start_period': '22:00:00',
            'end_period': '06:00:00'
        }
        self.client.post('/price-rules/', format='json', data=price_rule_stand)
        self.client.post(
            '/price-rules/', format='json', data=price_rule_reduced
        )

        call_record_start = {
            'type': 1,
            'timestamp': '2018-6-15 05:22:00',
            'call_id': 1,
            'source': '11986091154',
            'destination': '11982220546'
        }

        call_record_end = {
            'type': 2,
            'timestamp': '2018-6-15 07:22:00',
            'call_id': 1
        }

        self.client.post(
            '/call-records/', format='json', data=call_record_start
        )
        self.client.post(
            '/call-records/', format='json', data=call_record_end
        )

    def test_get_bill_by_month(self):
        response = self.client.get('/bills/11986091154/?month=6&year=2018')

        expected = {
            'month': 6,
            'year': 2018,
            'full_amount': 7.74,
            'records': [
                {
                    'destination': '11982220546',
                    'start': '2018-06-15T05:22:00',
                    'end': '2018-06-15T07:22:00',
                    'duration': '02h00m00s',
                    'call_cost': '7.74'
                }
            ]
        }

        expected_content = json.dumps(expected, separators=(',', ':')).encode()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, expected_content)

    def test_get_bill_by_month_exception(self):
        today = datetime.now()
        month = today.month
        year = today.year

        response = self.client.get(
            '/bills/11986091154/?month={}&year={}'.format(
                month, year
            )
        )

        expected = {
            "error": "The bill to this month isn't closed yet"
        }
        expected_content = json.dumps(expected, separators=(',', ':')).encode()

        self.assertEqual(
            response.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(response.content, expected_content)
