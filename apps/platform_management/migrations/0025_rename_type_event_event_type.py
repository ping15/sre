# Generated by Django 3.2.4 on 2024-08-20 06:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("platform_management", "0024_event_instructor"),
    ]

    operations = [
        migrations.RenameField(
            model_name="event",
            old_name="type",
            new_name="event_type",
        ),
    ]
