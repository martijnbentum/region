# Generated by Django 2.2.6 on 2020-01-31 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_auto_20200131_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='JiNMgQiHlTOf', max_length=12, unique=True),
        ),
    ]
