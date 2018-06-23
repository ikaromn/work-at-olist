from django.db import models

class CallRecord(models.Model):
    type = models.CharField(max_length=10)
    timestamp = models.DateTimeField(null=True)
    call_id = models.IntegerField()
    source = models.CharField(max_length=13, null=True)
    destination = models.CharField(max_length=13, null=True)

    class Meta:
        verbose_name = 'Call Record'
        verbose_name_plural = 'Call Records'