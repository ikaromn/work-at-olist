import logging
from decimal import Decimal
from rest_framework import views
from rest_framework import generics
from rest_framework.response import Response
from .models import Bill
from .models import PriceRule
from .models import CallRecord
from .schemas import bill_by_month_schema
from .validators import BillDateValidator
from .serializers import CallRecordSerializer
from .serializers import BillSerializer
from .serializers import PriceRuleSerializer

logger = logging.getLogger('call_center')


class CallRecordCreate(generics.CreateAPIView):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer


class BillByMonth(views.APIView):
    data_to_serialize = ''
    date_validator = BillDateValidator()
    schema = bill_by_month_schema()

    def get(self, request, **kwargs):
        """
        Endpoint to return the bill with all call records in the last month
        or the month and year gived
        """
        try:
            self.data_to_serialize = self._get_bill_by_month(
                source=kwargs['phone_number'])

            serializer = self.serializer_data()
            full_amount = self._sum_the_amount(serializer.data)

            logger.info(
                'The bill information was returned to phone number {}'.format(
                    kwargs['phone_number']
                )
            )
            return Response({
                'month': self.date_dict['month'],
                'year': self.date_dict['year'],
                'full_amount': full_amount,
                'records': serializer.data,
            })
        except Exception as e:
            logger.warn("Some error was ocurred: {}".format(str(e)))
            return Response({
                'error': str(e)
            }, status=422)

    def _get_bill_by_month(self, **kwargs):
        self.date_dict = self.date_validator.validate_bill_date(
            self.request.query_params.get('month', None),
            self.request.query_params.get('year', None)
        )

        logger.debug(
            'Get the bill with month {} and'
            ' year {} to phone number {}'.format(
                self.date_dict['month'],
                self.date_dict['year'],
                kwargs['source']
            )
        )
        return Bill.objects.filter(
            call_record__source=kwargs['source'],
            month=self.date_dict['month'],
            year=self.date_dict['year'])

    def serializer_data(self):
        return BillSerializer(self.data_to_serialize, many=True)

    def _sum_the_amount(self, cost):
        amount = Decimal('0.0')

        for i in cost:
            amount += Decimal(i['call_cost'])

        return amount


class PriceRuleListCreate(generics.ListCreateAPIView):
    queryset = PriceRule.objects.all()
    serializer_class = PriceRuleSerializer


class PriceRuleUpdate(generics.UpdateAPIView):
    queryset = PriceRule.objects.all()
    serializer_class = PriceRuleSerializer
