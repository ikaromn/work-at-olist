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
            'New bill registry should be saved '
            'with informations: source: {}, '
            'cost: {}, '
            'call start: {}, '
            'call end: {}, '
            'month: {}, '
            'year: {}'.format(
                str(self.call_record),
                self.call_cost,
                self.fk_call_start,
                self.fk_call_end,
                self.month,
                self.year
            )
        )

        try:
            self.save()
            logger.info('A new bill registry was saved: ID {}'.format(self.pk))
        except Exception as e:
            logger.warn(
                'Something wrong happened when '
                'saved a bill record: {}'.format(str(e))
            )

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
