# Generated by Django 3.2.12 on 2024-08-27 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teaching_space', '0007_auto_20240821_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingclass',
            name='publish_type',
            field=models.CharField(choices=[('none', '未发布'), ('publish_advertisement', '发布广告'), ('designate_instructor', '指定讲师')], default='none', max_length=24, verbose_name='发布方式'),
        ),
    ]
