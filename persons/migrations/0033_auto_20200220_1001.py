# Generated by Django 2.2.9 on 2020-02-20 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0032_auto_20200219_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='function',
            field=models.ManyToManyField(blank=True, to='persons.Function'),
        ),
    ]
