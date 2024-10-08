# Generated by Django 3.2.4 on 2024-08-05 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("platform_management", "0015_auto_20240805_1045"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coursetemplate",
            name="exam_duration",
            field=models.IntegerField(
                choices=[("45", "45分钟"), ("60", "60分钟"), ("120", "120分钟")],
                verbose_name="考试时长",
            ),
        ),
    ]
