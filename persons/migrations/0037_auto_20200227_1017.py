# Generated by Django 2.2.9 on 2020-02-27 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0036_auto_20200227_1015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='function',
        ),
        migrations.DeleteModel(
            name='Function',
        ),
    ]