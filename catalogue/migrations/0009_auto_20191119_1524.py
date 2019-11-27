# Generated by Django 2.2.6 on 2019-11-19 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20191119_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='geonameid',
            field=models.CharField(default='zYEEzCdAtxRW', max_length=12, unique=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='residence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogue.Location'),
        ),
    ]
