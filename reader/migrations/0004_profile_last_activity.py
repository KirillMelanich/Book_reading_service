# Generated by Django 4.2.7 on 2023-11-23 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0003_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_activity',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
