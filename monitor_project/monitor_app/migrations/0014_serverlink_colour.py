# Generated by Django 3.0.6 on 2020-06-10 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_app', '0013_remove_serverlink_testname'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverlink',
            name='colour',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
