# Generated by Django 2.2.9 on 2020-02-19 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0034_auto_20200219_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=735263468319, unique=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=869348121781, unique=True),
        ),
    ]
