# Generated by Django 2.2.6 on 2020-01-10 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_auto_20200103_1151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publisher',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='start_date',
        ),
        migrations.AddField(
            model_name='publisher',
            name='start_end_date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogue.Date'),
        ),
        migrations.AlterField(
            model_name='periodical',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='locations.UserLoc'),
        ),
        migrations.AlterField(
            model_name='person',
            name='birth_death_date',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogue.Date'),
        ),
        migrations.AlterField(
            model_name='person',
            name='place_of_birth',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='born', to='locations.UserLoc'),
        ),
        migrations.AlterField(
            model_name='person',
            name='place_of_death',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='died', to='locations.UserLoc'),
        ),
        migrations.AlterField(
            model_name='personlocationrelation',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.UserLoc'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='locations.UserLoc'),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='location',
            field=models.ManyToManyField(blank=True, null=True, to='locations.UserLoc'),
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
