# Generated by Django 3.2.4 on 2024-07-30 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("platform_management", "0007_clientapprovalslip"),
    ]

    operations = [
        migrations.AddField(
            model_name="instructor",
            name="id_photo",
            field=models.JSONField(default=dict, verbose_name="证件照"),
        ),
    ]
