# Generated by Django 2.2.6 on 2020-01-03 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20200103_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='hmnjuLVnkPPn', max_length=12, unique=True),
        ),
        migrations.AlterField(
            model_name='geoloc',
            name='user_locs',
            field=models.ManyToManyField(to='locations.UserLoc'),
        ),
    ]