# Generated by Django 4.1 on 2022-09-05 05:36

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0007_rename_team_leader_teams_team_leader'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Media',
            new_name='MediaStore',
        ),
    ]
