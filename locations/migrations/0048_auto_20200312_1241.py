# Generated by Django 2.2.10 on 2020-03-12 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0047_auto_20200304_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='LCSXNWZrrBNJ', max_length=12, unique=True),
        ),
    ]