# Generated by Django 2.2.6 on 2020-01-31 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20200131_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='qcueHqcGbBxG', max_length=12, unique=True),
        ),
    ]