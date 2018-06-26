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

    class Meta:
        verbose_name = 'Call Record'
        verbose_name_plural = 'Call Records'
        unique_together = (('type', 'call_id'))


class Bill(models.Model):
    call_record = models.ForeignKey(CallRecord, related_name='bills', on_delete=models.CASCADE)
    call_duration = models.TimeField()
    call_cost = models.FloatField()

    class Meta:
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'