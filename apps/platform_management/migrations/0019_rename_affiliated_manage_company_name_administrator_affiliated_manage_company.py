# Generated by Django 3.2.4 on 2024-08-06 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "platform_management",
            "0018_alter_administrator_affiliated_manage_company_name",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="administrator",
            old_name="affiliated_manage_company_name",
            new_name="affiliated_manage_company",
        ),
    ]
