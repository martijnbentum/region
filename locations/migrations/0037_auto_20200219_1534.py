# Generated by Django 2.2.9 on 2020-02-19 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0036_auto_20200219_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='rNTwCtsQCOqe', max_length=12, unique=True),
        ),
    ]