# Generated by Django 2.2.6 on 2019-11-21 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_auto_20191121_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='geonameid',
            field=models.CharField(default='mtAGiVqrTGkM', max_length=12, unique=True),
        ),
    ]