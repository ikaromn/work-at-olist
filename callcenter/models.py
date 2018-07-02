from django.db import models

TYPE_CHOICES = (
    (1, 'start'),
    (2, 'end')
)


class CallRecord(models.Model):
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
    call_duration = models.TimeField()
    call_cost = models.FloatField()

    def create(self, **kwargs):
        self.call_record = kwargs['bill_data']['call']
        self.call_cost = kwargs['bill_data']['cost']
        self.call_duration = str(kwargs['bill_data']['call_duration'])

        self.save()

    class Meta:
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'
