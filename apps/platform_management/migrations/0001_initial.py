# Generated by Django 3.2.4 on 2024-07-04 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='attachment/')),
            ],
        ),
        migrations.CreateModel(
            name='CourseTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=32, verbose_name='课程名称')),
                ('level', models.CharField(max_length=32, verbose_name='级别')),
                ('abbreviation', models.CharField(max_length=32, verbose_name='英文缩写')),
                ('num_lessons', models.IntegerField(verbose_name='课时数量')),
                ('version', models.CharField(max_length=16, verbose_name='版本')),
                ('release_date', models.DateField(verbose_name='上线日期')),
                ('status', models.CharField(max_length=32, verbose_name='状态')),
                ('assessment_method', models.CharField(max_length=16, verbose_name='考核方式')),
                ('attachments', models.JSONField(default=list, verbose_name='附件区域')),
                ('certification', models.CharField(max_length=32, verbose_name='认证证书')),
                ('trainees_count', models.IntegerField(verbose_name='培训人次')),
                ('client_company_count', models.IntegerField(verbose_name='客户数')),
                ('class_count', models.IntegerField(verbose_name='开班次数')),
                ('num_instructors', models.IntegerField(verbose_name='讲师数量')),
                ('material_content', models.TextField(verbose_name='教材内容')),
                ('course_overview', models.TextField(verbose_name='课程概述')),
                ('target_students', models.TextField(verbose_name='目标学员')),
                ('learning_objectives', models.TextField(verbose_name='学习目标')),
                ('learning_benefits', models.TextField(verbose_name='学习收益')),
                ('course_content', models.JSONField(default=list, verbose_name='课程内容')),
                ('remarks', models.TextField(verbose_name='备注')),
                ('exam_type', models.JSONField(default=list, verbose_name='考试题型')),
                ('num_questions', models.IntegerField(verbose_name='考题数量')),
                ('exam_duration', models.IntegerField(verbose_name='考试时长')),
                ('exam_language', models.CharField(max_length=8, verbose_name='考试语言')),
                ('passing_score', models.IntegerField(verbose_name='过线分数')),
                ('require_authorized_training', models.BooleanField(verbose_name='是否要求授权培训')),
                ('certification_body', models.JSONField(default=list, verbose_name='认证机构')),
            ],
        ),
    ]
