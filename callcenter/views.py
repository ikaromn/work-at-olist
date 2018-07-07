import logging
import coreapi
from datetime import datetime
from rest_framework import generics, views, schemas
from rest_framework.response import Response
from .models import CallRecord, Bill, PriceRule
from .serializers import\
    CallRecordSerializer, BillSerializer, PriceRuleSerializer
from .validators import BillDateValidator
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
    date_validator = BillDateValidator()
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
                description="The month of the bill",
                type="int"
            ),
            coreapi.Field(
                "year",
                required=False,
                location="query",
                description="The year of the bill",
                type="int"
            ),
        ])

    def get(self, request, **kwargs):
        """
        Endpoint to return the bill with all call records in the last month
        or the month and year gived
        """
        try:
            self.data_to_serialize = self.__get_bill_by_month(
                source=kwargs['phone_number'])

            serializer = self.serializer_data()
            full_amount = self.__sum_the_amount(serializer.data)

            return Response({
                'month': self.date_dict['month'],
                'year': self.date_dict['year'],
                'full_amount': full_amount,
                'records': serializer.data,
            })
        except Exception as e:
            return Response({
                'error': str(e)
            })

    def serializer_data(self):
        return BillSerializer(self.data_to_serialize, many=True)

    def __get_bill_by_month(self, **kwargs):
        self.date_dict = self.date_validator.validate_bill_date(
            self.request.query_params.get('month', None),
            self.request.query_params.get('year', None)
        )

        return Bill.objects.filter(
            call_record__source=kwargs['source'],
            month=self.date_dict['month'],
            year=self.date_dict['year'])

    def __sum_the_amount(self, cost):
        amount = 0

        for i in cost:
            amount += i['call_cost']

        return amount


class PriceRuleListCreate(generics.ListCreateAPIView):
    queryset = PriceRule.objects.all()
    serializer_class = PriceRuleSerializer


class PriceRuleUpdate(generics.UpdateAPIView):
    queryset = PriceRule.objects.all()
    serializer_class = PriceRuleSerializer
