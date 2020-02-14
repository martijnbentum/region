# Generated by Django 2.2.9 on 2020-02-14 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0020_auto_20200214_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='function',
            field=models.ManyToManyField(blank=True, to='persons.Function'),
        ),
        migrations.AlterField(
            model_name='personillustrationrelationrole',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='persontextrelationrole',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]