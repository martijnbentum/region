# Generated by Django 2.2.10 on 2020-03-18 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0052_auto_20200318_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='jFJDSGBBrmJl', max_length=12, unique=True),
        ),
    ]
