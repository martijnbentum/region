# Generated by Django 2.2.9 on 2020-02-27 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0042_auto_20200227_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=754191759785, unique=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=345571497763, unique=True),
        ),
    ]
