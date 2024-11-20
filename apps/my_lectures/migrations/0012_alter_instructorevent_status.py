from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_lectures', '0011_auto_20241112_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructorevent',
            name='status',
            field=models.CharField(
                choices=[('pending', '待处理'), ('agreed', '已同意'), ('rejected', '已拒绝'), ('removed', '已指定其他讲师'),
                         ('timeout', '已超时'), ('finished', '已完成'), ('revoke', '已撤销')],
                default='pending', max_length=50, verbose_name='状态'),
        ),
    ]
