# Generated by Django 2.2.6 on 2019-11-19 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20191119_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='geonameid',
            field=models.CharField(default='fAkNOJPEEZlW', max_length=12, unique=True),
        ),
    ]