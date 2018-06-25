from rest_framework import generics, views
from rest_framework.response import Response
from .models import CallRecord
from .serializers import CallRecordSerializer
from datetime import datetime


class CallRecordCreate(generics.CreateAPIView):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer


class BillByMonth(views.APIView):
    data_to_serialize = ''

    def get(self, request, **kwargs):
        if kwargs['month']:
            self.data_to_serialize = self.get_bill(
                source=kwargs['phone_number'],
                month=kwargs['month'],
                year=kwargs['year'])

            serializer = self.serializer_data()

            return Response(serializer.data)

        last_month = (datetime.now().month) - 1
        current_year = datetime.now().year

        self.data_to_serialize = self.get_bill(
            source=kwargs['phone_number'],
            month=last_month,
            year=current_year)

        serializer = self.serializer_data()

        return Response(serializer.data)

    def serializer_data(self):
        return CallRecordSerializer(self.data_to_serialize, many=True)

    def get_bill(self, **kwargs):
        return CallRecord.objects.filter(
            source=kwargs['source'],
            timestamp__month=kwargs['month'],
            timestamp__year=kwargs['year'])
