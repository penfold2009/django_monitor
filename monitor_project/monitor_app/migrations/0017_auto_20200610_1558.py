# Generated by Django 3.0.6 on 2020-06-10 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_app', '0016_auto_20200610_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverlink',
            name='colour',
            field=models.CharField(blank=True, default='grey', max_length=200, null=True),
        ),
    ]
