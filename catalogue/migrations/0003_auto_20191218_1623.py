# Generated by Django 2.2.6 on 2019-12-18 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_auto_20191218_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='geonameid',
            field=models.CharField(default='gsFVjZidfEGJ', max_length=12, unique=True),
        ),
    ]