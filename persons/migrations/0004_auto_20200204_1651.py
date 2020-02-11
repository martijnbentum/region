# Generated by Django 2.2.9 on 2020-02-04 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0003_person_function'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pseudonym',
            name='person',
        ),
        migrations.AddField(
            model_name='person',
            name='pseudonym',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='persons.Pseudonym'),
        ),
        migrations.AlterField(
            model_name='person',
            name='function',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='persons.Function'),
        ),
        migrations.AlterField(
            model_name='pseudonym',
            name='name',
            field=models.CharField(max_length=300),
        ),
    ]