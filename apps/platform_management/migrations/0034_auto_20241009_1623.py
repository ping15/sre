# Generated by Django 3.2.12 on 2024-10-09 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platform_management', '0033_auto_20240926_1801'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='administrator',
            options={'verbose_name': '管理员', 'verbose_name_plural': '管理员'},
        ),
        migrations.AlterModelOptions(
            name='clientapprovalslip',
            options={'verbose_name': '客户资料审批', 'verbose_name_plural': '客户资料审批'},
        ),
        migrations.AlterModelOptions(
            name='clientcompany',
            options={'verbose_name': '客户公司', 'verbose_name_plural': '客户公司'},
        ),
        migrations.AlterModelOptions(
            name='clientstudent',
            options={'verbose_name': '客户学员', 'verbose_name_plural': '客户学员'},
        ),
        migrations.AlterModelOptions(
            name='coursetemplate',
            options={'ordering': ['-id'], 'verbose_name': '课程模板', 'verbose_name_plural': '课程模板'},
        ),
        migrations.AlterModelOptions(
            name='instructor',
            options={'verbose_name': '讲师', 'verbose_name_plural': '讲师'},
        ),
        migrations.AlterModelOptions(
            name='managecompany',
            options={'verbose_name': '管理公司', 'verbose_name_plural': '管理公司'},
        ),
        migrations.AlterField(
            model_name='managecompany',
            name='type',
            field=models.CharField(
                choices=[('default', '默认公司'), ('partner', '合作伙伴')],
                default='partner', max_length=32, verbose_name='类型'),
        ),
    ]