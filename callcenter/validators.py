from .models import CallRecord

START_TYPE = 1
END_TYPE = 2


class BillValidator:
    def validate_bill_to_record(self, **kwargs):
        call_data = kwargs['call_data']

        if call_data['type'] == 2:
            return self.__existent_start_type(call_data['call_id'])

        return False

    def __existent_start_type(self, call_id):
        if CallRecord.objects.filter(
            type=START_TYPE, call_id=call_id
        ).exists():

            return True

        return False

    def prepare_bill_data(self, call_record_data):
        call_id = call_record_data['call_id']
        start_call_datetime = CallRecord.objects.get(
            call_id=call_id, type=START_TYPE
        ).timestamp

        end_call_datetime = call_record_data['timestamp']
        call_duration = end_call_datetime - start_call_datetime
        cost = 12.76

        bill_data = {}
        bill_data['call'] = CallRecord.objects.get(
            call_id=call_id, type=START_TYPE
        )

        bill_data['cost'] = cost
        bill_data['call_duration'] = call_duration

        return bill_data
