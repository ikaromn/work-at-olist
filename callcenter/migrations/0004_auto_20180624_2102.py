# Generated by Django 2.0.6 on 2018-06-24 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('callcenter', '0003_auto_20180624_2049'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='callrecord',
            unique_together={('type', 'call_id')},
        ),
    ]
