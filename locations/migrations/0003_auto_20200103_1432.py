# Generated by Django 2.2.6 on 2020-01-03 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_auto_20200103_1152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geoloc',
            name='user_loc',
        ),
        migrations.AddField(
            model_name='geoloc',
            name='user_locs',
            field=models.ManyToManyField(blank=True, null=True, to='locations.UserLoc'),
        ),
        migrations.AlterField(
            model_name='geoloc',
            name='geonameid',
            field=models.CharField(default='lhQxbXwMhMeZ', max_length=12, unique=True),
        ),
    ]