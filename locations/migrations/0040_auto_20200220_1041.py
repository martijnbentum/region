# Generated by Django 2.2.9 on 2020-02-20 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0039_auto_20200220_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='zQVaDJKvKQCX', max_length=12, unique=True),
        ),
    ]