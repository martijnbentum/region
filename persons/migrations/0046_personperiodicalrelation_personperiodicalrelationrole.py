# Generated by Django 2.2.10 on 2020-04-06 14:15

from django.db import migrations, models
import django.db.models.deletion
import utils.model_util


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0065_auto_20200406_1615'),
        ('persons', '0045_auto_20200326_1618'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonPeriodicalRelationRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            bases=(models.Model, utils.model_util.info),
        ),
        migrations.CreateModel(
            name='PersonPeriodicalRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodical', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Periodical')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Person')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.PersonPeriodicalRelationRole')),
            ],
            bases=(models.Model, utils.model_util.info),
        ),
    ]