# Generated by Django 2.2.9 on 2020-02-11 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0016_auto_20200211_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='DYCMsaTUoqzB', max_length=12, unique=True),
        ),
    ]
