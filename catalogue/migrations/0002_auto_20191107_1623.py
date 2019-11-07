# Generated by Django 2.2.6 on 2019-11-07 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='location',
            name='status',
            field=models.CharField(choices=[('F', 'fiction'), ('NF', 'non-fiction')], default='NF', max_length=2),
        ),
        migrations.AlterField(
            model_name='locationtype',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
