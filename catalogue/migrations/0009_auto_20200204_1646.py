# Generated by Django 2.2.9 on 2020-02-04 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20200204_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=188347397664, unique=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=325672213579, unique=True),
        ),
    ]
