# Generated by Django 3.2.12 on 2025-01-09 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_management', '0039_auto_20241101_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrator',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='freq_interval',
            field=models.JSONField(default=list, verbose_name='周期频率'),
        ),
        migrations.AlterField(
            model_name='event',
            name='freq_type',
            field=models.CharField(
                blank=True,
                choices=[('weekly', '每周'),
                         ('biweekly', '每两周'),
                         ('monthly', '每月')],
                max_length=16,
                null=True,
                verbose_name='周期类型'
            ),
        ),
    ]
