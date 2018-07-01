from django.test import TestCase
from model_mommy import mommy
from .models import CallRecord


class CallRecordTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.call_record = mommy.make(
            CallRecord, type=2, timestamp='2018-11-25 08:08:08',
            call_id=50, source='', destination=''
        )

    def test_call_record_creation(self):
        self.assertTrue(isinstance(self.call_record, CallRecord))
        self.assertEquals(self.call_record.type, 2)
        self.assertEquals(self.call_record.call_id, 50)
        self.assertEquals(self.call_record.timestamp, '2018-11-25 08:08:08')
