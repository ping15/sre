# Generated by Django 3.2.4 on 2024-07-26 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teaching_space", "0003_alter_trainingclass_course_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainingclass",
            name="review",
            field=models.TextField(default="", verbose_name="课后复盘"),
        ),
    ]
