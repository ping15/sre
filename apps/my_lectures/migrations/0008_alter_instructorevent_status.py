# Generated by Django 3.2.12 on 2024-09-12 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_lectures', '0007_instructorevent_event_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructorevent',
            name='status',
            field=models.CharField(
                choices=[('pending', '待处理'), ('agreed', '已同意'),
                         ('rejected', '已拒绝'), ('removed', '已指定其他讲师'),
                         ('timeout', '已超时'), ('finished', '已完成')],
                default='pending', max_length=50, verbose_name='状态'),
        ),
    ]
