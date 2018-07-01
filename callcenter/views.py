import logging
from datetime import datetime
from rest_framework import generics, views
from rest_framework.response import Response
from .models import CallRecord, Bill
from .serializers import CallRecordSerializer, BillSerializer

logger = logging.getLogger(__name__)


class CallRecordCreate(generics.CreateAPIView):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer


class BillByMonth(views.APIView):
    data_to_serialize = ''

    def get(self, request, **kwargs):
        if kwargs['month']:
            self.data_to_serialize = self.__get_bill(
                source=kwargs['phone_number'],
                month=kwargs['month'],
                year=kwargs['year']
            )

            serializer = self.serializer_data()

            return Response({
                'records': serializer.data,
            })

        last_month = (datetime.now().month) - 1
        current_year = datetime.now().year

        self.data_to_serialize = self.__get_bill(
            source=kwargs['phone_number'],
            month=last_month,
            year=current_year)

        serializer = self.serializer_data()

        return Response({
            'records': serializer.data,
        })

    def serializer_data(self):
        return BillSerializer(self.data_to_serialize, many=True)

    def __get_bill(self, **kwargs):
        return Bill.objects.filter(
            call_record__source=kwargs['source'],
            call_record__timestamp__month=kwargs['month'],
            call_record__timestamp__year=kwargs['year'],
            call_record__type=1)
