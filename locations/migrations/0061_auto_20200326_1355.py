# Generated by Django 2.2.10 on 2020-03-26 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0060_auto_20200325_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='VZHMIAEeRaYL', max_length=12, unique=True),
        ),
    ]
