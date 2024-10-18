# Generated by Django 3.2.4 on 2024-08-06 15:08
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("platform_management", "0017_auto_20240806_1714"),
    ]

    operations = [
        migrations.AlterField(
            model_name="administrator",
            name="affiliated_manage_company_name",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="platform_management.managecompany",
                verbose_name="管理公司",
            ),
        ),
    ]
