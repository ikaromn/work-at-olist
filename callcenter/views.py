import logging
import coreapi
from datetime import datetime
from rest_framework import generics, views, schemas
from rest_framework.response import Response
from .models import CallRecord, Bill
from .serializers import CallRecordSerializer, BillSerializer
from django.conf.urls import url
from rest_framework.decorators import\
    api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer


@api_view()
@permission_classes((AllowAny, ))
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):

    generator = schemas.SchemaGenerator(title='Bill API')

    return Response(generator.get_schema())


logger = logging.getLogger(__name__)


class CallRecordCreate(generics.CreateAPIView):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer


class BillByMonth(views.APIView):
    data_to_serialize = ''
    schema = schemas.AutoSchema(manual_fields=[
            coreapi.Field(
                "phone_number",
                required=True,
                location="path",
                description="The phone number to get the bill"
            ),
            coreapi.Field(
                "month",
                required=False,
                location="query",
                description="The month of the bill"
            ),
            coreapi.Field(
                "year",
                required=False,
                location="query",
                description="The year of the bill"
            ),
        ])

    def get(self, request, **kwargs):
        """
        Endpoint to return the bill with all call records in the last month
        or the month and year gived
        """
        if self.request.query_params.get('month', None):
            self.data_to_serialize = self.__get_bill(
                source=kwargs['phone_number'],
                month=self.request.query_params.get('month', None),
                year=self.request.query_params.get('year', None)
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
