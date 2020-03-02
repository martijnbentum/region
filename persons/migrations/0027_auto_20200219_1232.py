# Generated by Django 2.2.9 on 2020-02-19 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0026_auto_20200219_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='function',
            field=models.ManyToManyField(blank=True, to='persons.Function'),
        ),
        migrations.AlterField(
            model_name='personlocationrelation',
            name='relation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='persons.LocationRelation'),
        ),
    ]