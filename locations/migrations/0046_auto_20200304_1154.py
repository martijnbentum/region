# Generated by Django 2.2.10 on 2020-03-04 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0045_auto_20200302_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='GNzrjZLBDfoV', max_length=12, unique=True),
        ),
    ]
