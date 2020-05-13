# Generated by Django 2.2.10 on 2020-05-13 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0047_persontextrelation_published_under'),
    ]

    operations = [
        migrations.AddField(
            model_name='movement',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='movement',
            name='complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='complete',
            field=models.BooleanField(default=False),
        ),
    ]
