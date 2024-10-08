# Generated by Django 3.2.4 on 2024-07-25 07:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("platform_management", "0002_auto_20240725_1535"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrainingClass",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "course_name",
                    models.CharField(max_length=64, unique=True, verbose_name="课程"),
                ),
                (
                    "session_number",
                    models.CharField(max_length=32, verbose_name="课程期数"),
                ),
                ("status", models.CharField(max_length=16, verbose_name="状态")),
                ("class_mode", models.CharField(max_length=16, verbose_name="上课模式")),
                ("student_count", models.IntegerField(default=0, verbose_name="学员数量")),
                ("start_date", models.DateField(verbose_name="开课时间")),
                (
                    "assessment_method",
                    models.CharField(max_length=16, verbose_name="考核方式"),
                ),
                ("certification", models.CharField(max_length=32, verbose_name="认证证书")),
                ("location", models.CharField(max_length=32, verbose_name="开课地点")),
                (
                    "target_client_company_name",
                    models.CharField(max_length=64, verbose_name="客户公司"),
                ),
                (
                    "hours_per_lesson",
                    models.IntegerField(default=6, verbose_name="课程课时"),
                ),
                (
                    "instructor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="training_classes",
                        to="platform_management.instructor",
                        verbose_name="讲师",
                    ),
                ),
            ],
        ),
    ]
