# Generated by Django 2.2.6 on 2019-11-15 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20191115_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='geonameid',
            field=models.CharField(default='VziDRMnGAsHd', max_length=12, unique=True),
        ),
    ]