# Generated by Django 2.2.9 on 2020-03-02 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0044_auto_20200227_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='ZnleMiTeYYRZ', max_length=12, unique=True),
        ),
    ]