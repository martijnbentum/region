from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('easyaudit', '0003_auto_20170228_1505'),
    ]

    # Restore the operation used by django-easy-audit 1.3.3. Version 1.3.9
    # rewrites it as AddIndex, duplicating the index in migration 0018's state.
    operations = [
        migrations.AlterIndexTogether(
            name='crudevent',
            index_together={('object_id', 'content_type')},
        ),
    ]
