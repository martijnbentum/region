# Generated by Django 2.2.9 on 2020-02-11 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0012_auto_20200211_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='function',
            field=models.ManyToManyField(blank=True, to='persons.Function'),
        ),
    ]
