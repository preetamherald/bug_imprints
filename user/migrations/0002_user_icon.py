# Generated by Django 4.1 on 2022-09-07 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='user_icons'),
        ),
    ]
