# Generated by Django 4.2.7 on 2023-11-23 12:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0004_profile_last_activity"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="total_reading_time",
            field=models.DurationField(default=datetime.timedelta),
        ),
    ]