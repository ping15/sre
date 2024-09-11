# Generated by Django 3.2.12 on 2024-09-03 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_lectures', '0005_auto_20240830_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructorenrolment',
            name='status',
            field=models.CharField(
                choices=[('accepted', '已聘用'), ('pending', '待聘用'), ('not_enrolled', '未报名'),
                         ('rejected', '未聘用'), ('timeout', '已过期')],
                default='pending',
                max_length=16),
        ),
        migrations.AlterField(
            model_name='instructorevent',
            name='created_datetime',
            field=models.DateTimeField(auto_now_add=True, verbose_name='发起时间'),
        ),
        migrations.AlterField(
            model_name='instructorevent',
            name='status',
            field=models.CharField(
                choices=[('pending', '待处理'), ('agreed', '已同意'), ('rejected', '已拒绝'),
                         ('removed', '已指定其他讲师'), ('timeout', '已超时')],
                default='pending',
                max_length=50,
                verbose_name='状态'),
        ),
    ]