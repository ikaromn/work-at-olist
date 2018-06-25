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
