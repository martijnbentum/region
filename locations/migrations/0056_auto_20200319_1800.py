# Generated by Django 2.2.10 on 2020-03-19 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0055_auto_20200319_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='OAXQwZoqNYFE', max_length=12, unique=True),
        ),
    ]
