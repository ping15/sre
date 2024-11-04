# Generated by Django 3.2.12 on 2024-11-01 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_management', '0037_auto_20241101_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientstudent',
            name='affiliated_client_company_name',
            field=models.CharField(max_length=128, verbose_name='客户公司'),
        ),
        migrations.AlterField(
            model_name='clientstudent',
            name='department',
            field=models.CharField(max_length=128, verbose_name='部门'),
        ),
        migrations.AlterField(
            model_name='clientstudent',
            name='position',
            field=models.CharField(max_length=128, verbose_name='职位'),
        ),
    ]
