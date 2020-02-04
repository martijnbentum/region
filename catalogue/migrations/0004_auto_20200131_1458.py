# Generated by Django 2.2.6 on 2020-01-31 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_auto_20200131_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=618651947116, unique=True),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='start_end_date',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utilities.Date'),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=234417867981, unique=True),
        ),
    ]
