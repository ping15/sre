# Generated by Django 3.2.12 on 2024-09-26 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_management', '0031_alter_coursetemplate_exam_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursetemplate',
            name='exam_language',
            field=models.CharField(
                blank=True, choices=[('chinese', '中文'), ('english', '英文')],
                max_length=8, null=True, verbose_name='考试语言'),
        ),
    ]