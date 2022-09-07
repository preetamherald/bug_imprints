# Generated by Django 4.1 on 2022-09-06 03:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0009_remove_bugduplicate_duplicate_id_bugduplicate_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teams',
            name='team_leader',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, related_name='%(class)s_team_leader', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
