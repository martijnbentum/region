# Generated by Django 2.2.9 on 2020-02-19 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0030_auto_20200219_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='function',
            field=models.ManyToManyField(blank=True, to='persons.Function'),
        ),
        migrations.AlterField(
            model_name='publishermanager',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manager', to='persons.Person'),
        ),
    ]
