# Generated by Django 2.2.10 on 2020-04-06 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0064_auto_20200402_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=266936436879),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=315637827376635539),
        ),
    ]
