# Generated by Django 3.0.6 on 2020-05-25 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_app', '0009_auto_20200520_1730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mibparameter',
            name='stateduration',
        ),
        migrations.RemoveField(
            model_name='mibparameter',
            name='statetimestart',
        ),
        migrations.RemoveField(
            model_name='mibparameter',
            name='transition_statetime',
        ),
        migrations.AddField(
            model_name='mibparameter',
            name='current_status',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='mibparameter',
            name='mib_status',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mibparameter',
            name='thresholdvalue',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
    ]
