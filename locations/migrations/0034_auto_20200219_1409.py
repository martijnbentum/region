# Generated by Django 2.2.9 on 2020-02-19 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0033_auto_20200219_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='xmTkEdVgPZAD', max_length=12, unique=True),
        ),
    ]
