# Generated by Django 3.2.12 on 2024-08-30 07:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_management', '0028_remove_coursetemplate_teaching_count'),
        ('my_lectures', '0004_alter_instructorevent_training_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructorevent',
            name='instructor',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='instructor_event', to='platform_management.instructor', verbose_name='讲师'),
        ),
        migrations.AddField(
            model_name='instructorevent',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='开课时间'),
        ),
        migrations.AlterField(
            model_name='instructorenrolment',
            name='status',
            field=models.CharField(
                choices=[('accepted', '已聘用'), ('pending', '待聘用'), ('rejected', '未聘用'), ('timeout', '已过期')],
                default='pending',
                max_length=16
            ),
        ),
        migrations.AlterField(
            model_name='instructorevent',
            name='status',
            field=models.CharField(
                choices=[('pending', '待处理'), ('agreed', '已同意'), ('rejected', '已拒绝'),
                         ('removed', '已被移除'), ('timeout', '已超时')],
                default='pending',
                max_length=50,
                verbose_name='状态'
            ),
        ),
    ]