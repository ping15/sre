# Generated by Django 3.2.12 on 2024-09-26 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_management', '0029_alter_event_training_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientapprovalslip',
            name='status',
            field=models.CharField(
                choices=[('pending', '待处理'), ('agreed', '同意'), ('rejected', '驳回')],
                default='pending', max_length=32, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='coursetemplate',
            name='release_date',
            field=models.DateField(blank=True, null=True, verbose_name='上线日期'),
        ),
        migrations.AlterField(
            model_name='coursetemplate',
            name='version',
            field=models.CharField(default='', max_length=16, verbose_name='版本'),
        ),
        migrations.AlterField(
            model_name='event',
            name='freq_type',
            field=models.CharField(
                blank=True, choices=[('weekly', '每周'), ('biweekly', '每两周'), ('monthly', '每月')],
                max_length=16, null=True),
        ),
    ]
