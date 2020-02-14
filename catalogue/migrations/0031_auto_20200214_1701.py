# Generated by Django 2.2.9 on 2020-02-14 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0030_auto_20200214_1554'),
    ]

    operations = [
        migrations.RenameField(
            model_name='illustration',
            old_name='context',
            new_name='notes',
        ),
        migrations.RemoveField(
            model_name='illustration',
            name='language',
        ),
        migrations.AddField(
            model_name='illustration',
            name='page_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=981627591921, unique=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=253463961878, unique=True),
        ),
    ]
