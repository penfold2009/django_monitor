# Generated by Django 3.0.6 on 2020-05-17 18:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('online', models.BooleanField(default=True)),
                ('lastupdate', models.DateTimeField(default=django.utils.timezone.now)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='monitor_app.Company')),
            ],
        ),
        migrations.CreateModel(
            name='ServerLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(default='up', max_length=20)),
                ('server', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='monitor_app.Server')),
            ],
        ),
        migrations.CreateModel(
            name='ServerIpAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(protocol='ipv4')),
                ('ping_status', models.BooleanField()),
                ('server', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='monitor_app.Server')),
            ],
        ),
        migrations.CreateModel(
            name='MIBParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transition_statetime', models.FloatField()),
                ('statetimestart', models.FloatField(default=1589741388.053614)),
                ('stateduration', models.FloatField()),
                ('name', models.CharField(max_length=20)),
                ('mib_parameter', models.CharField(max_length=20)),
                ('mibtype', models.CharField(default='statechange', max_length=20)),
                ('thresholdvalue', models.FloatField()),
                ('correctthresholdvalue', models.FloatField()),
                ('parent_link', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='monitor_app.ServerLink')),
            ],
        ),
        migrations.CreateModel(
            name='Emails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=20)),
                ('server', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='monitor_app.Server')),
            ],
        ),
    ]
