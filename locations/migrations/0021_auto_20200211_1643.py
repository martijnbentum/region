# Generated by Django 2.2.9 on 2020-02-11 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0020_auto_20200211_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='pInZhGylkZvH', max_length=12, unique=True),
        ),
    ]
