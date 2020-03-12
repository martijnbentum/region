# Generated by Django 2.2.10 on 2020-03-04 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0045_auto_20200302_1449'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='upload',
            new_name='pdf',
        ),
        migrations.RemoveField(
            model_name='text',
            name='upload',
        ),
        migrations.AddField(
            model_name='illustrationpublicationrelation',
            name='page',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='publication',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to='publication/'),
        ),
        migrations.AddField(
            model_name='textpublicationrelation',
            name='end_page',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='textpublicationrelation',
            name='start_page',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication_id',
            field=models.IntegerField(default=927735469526, unique=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='text_id',
            field=models.IntegerField(default=688494963663295977),
        ),
    ]