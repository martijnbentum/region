# Generated by Django 2.2.10 on 2020-03-12 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0047_auto_20200304_1159'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Type',
            new_name='PublicationType',
        ),
        migrations.RenameField(
            model_name='texttextrelationtype',
            old_name='description',
            new_name='notes',
        ),
        migrations.AlterField(
            model_name='illustration',
            name='upload',
            field=models.ImageField(blank=True, null=True, upload_to='illustrations/'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=652476376192, unique=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=499956186474284913),
        ),
    ]
