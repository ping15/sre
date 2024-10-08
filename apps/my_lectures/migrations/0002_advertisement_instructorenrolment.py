# Generated by Django 3.2.12 on 2024-08-27 08:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teaching_space', '0007_auto_20240821_1549'),
        ('platform_management', '0027_coursetemplate_teaching_count'),
        ('my_lectures', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolment_count', models.IntegerField(default=0, verbose_name='报名人数')),
                ('deadline_datetime', models.DateTimeField(verbose_name='报名截至时间')),
                ('location', models.CharField(max_length=255, verbose_name='开课地点')),
                ('training_class', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                                        related_name='advertisement',
                                                        to='teaching_space.trainingclass',
                                                        verbose_name='培训班')),
            ],
            options={
                'verbose_name': '广告',
                'verbose_name_plural': '广告',
            },
        ),
        migrations.CreateModel(
            name='InstructorEnrolment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[('accepted', '已聘用'), ('pending', '待聘用'), ('rejected', '未聘用')],
                    default='pending',
                    max_length=16)),
                ('advertisement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                    related_name='instructor_enrolments',
                                                    to='my_lectures.advertisement', verbose_name='广告')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                 related_name='enrolments',
                                                 to='platform_management.instructor', verbose_name='讲师')),
            ],
        ),
    ]
