import logging
import json
from django.db import models

logger = logging.getLogger('call_center')


class CallRecord(models.Model):
    TYPE_CHOICES = (
        (1, 'start'),
        (2, 'end')
    )
    type = models.IntegerField(choices=TYPE_CHOICES)
    timestamp = models.DateTimeField(null=True)
    call_id = models.IntegerField()
    source = models.CharField(max_length=13, null=True)
    destination = models.CharField(max_length=13, null=True)

    def __str__(self):
        return str(self.source)

    class Meta:
        verbose_name = 'Call Record'
        verbose_name_plural = 'Call Records'
        unique_together = (('type', 'call_id'))


class Bill(models.Model):
    call_record = models.ForeignKey(
        CallRecord, related_name='bills', on_delete=models.CASCADE
    )
    call_cost = models.DecimalField(max_digits=7, decimal_places=2)
    fk_call_start = models.DateTimeField(null=False)
    fk_call_end = models.DateTimeField(null=False)
    month = models.IntegerField()
    year = models.IntegerField()

    def create(self, **kwargs):
        self.call_record = kwargs['bill_data']['call']
        self.call_cost = kwargs['bill_data']['cost']
        self.fk_call_start = str(kwargs['bill_data']['call_start'])
        self.fk_call_end = str(kwargs['bill_data']['call_end'])
        self.month = kwargs['bill_data']['month']
        self.year = kwargs['bill_data']['year']

        logger.debug(
            'Bill Registry to be saved', extra={
                'event': 'BillCreateRegistry',
                'source': str(self.call_record),
                'cost': float(self.call_cost),
                'call_start': self.fk_call_start,
                'call_end': self.fk_call_end,
                'month': self.month,
                'year': self.year
            })

        try:
            self.save()
            logger.info('Bill Registry', extra={
                'event': 'BillCreateRegistry',
                'id': self.pk
            })
        except Exception as e:
            logger.warn('Bill Registry error', extra={
                'event': 'BillRegistryCreateError',
                'error': str(e)
            })

            return str(e)

    class Meta:
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'


class PriceRule(models.Model):
    PRICE_RULE_TYPE = (
        (1, 'standart'),
        (2, 'reduced')
    )
    rule_type = models.IntegerField(choices=PRICE_RULE_TYPE, unique=True)
    fixed_charge = models.DecimalField(max_digits=7, decimal_places=2)
    call_charge = models.DecimalField(max_digits=7, decimal_places=2)
    start_period = models.TimeField()
    end_period = models.TimeField()

    class Meta:
        verbose_name = 'Price rule'
        verbose_name_plural = 'Price rules'
