# Generated by Django 2.2.9 on 2020-02-27 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0037_auto_20200227_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='sex',
            field=models.CharField(choices=[('F', 'female'), ('M', 'male'), ('O', 'other'), ('U', 'unknown')], max_length=1),
        ),
    ]