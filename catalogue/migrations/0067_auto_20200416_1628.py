# Generated by Django 2.2.10 on 2020-04-16 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0066_auto_20200408_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=996528645754),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=842516758375319688),
        ),
    ]
