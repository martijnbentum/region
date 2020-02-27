# Generated by Django 2.2.9 on 2020-02-27 09:15

from django.db import migrations, models
import utils.model_util


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0035_auto_20200227_1012'),
    ]

    operations = [
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            bases=(models.Model, utils.model_util.info),
        ),
        migrations.AddField(
            model_name='person',
            name='function',
            field=models.ManyToManyField(blank=True, to='persons.Function'),
        ),
    ]
