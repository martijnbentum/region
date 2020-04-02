# Generated by Django 2.2.10 on 2020-04-02 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0066_auto_20200402_1356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userloc',
            name='info',
        ),
        migrations.AddField(
            model_name='geoloc',
            name='info',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='UHXpjSkrKfNn', max_length=12, unique=True),
        ),
    ]
