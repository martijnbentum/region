# Generated by Django 2.2.10 on 2020-04-18 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0070_auto_20200416_1628'),
    ]

    operations = [
        migrations.RenameField(
            model_name='geoloc',
            old_name='info',
            new_name='information',
        ),
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='aPFrsnAYdYHZ', max_length=12, unique=True),
        ),
    ]
