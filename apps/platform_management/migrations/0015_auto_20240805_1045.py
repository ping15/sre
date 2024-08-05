# Generated by Django 3.2.4 on 2024-08-05 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "platform_management",
            "0014_merge_0012_auto_20240802_1105_0013_auto_20240804_1221",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="clientapprovalslip",
            name="status",
            field=models.CharField(
                choices=[("pending", "待处理"), ("approval", "同意"), ("rejected", "驳回")],
                default="pending",
                max_length=32,
                verbose_name="状态",
            ),
        ),
        migrations.AlterField(
            model_name="clientcompany",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("public_card", "刷公务卡"),
                    ("telegraphic_transfer", "电汇"),
                    ("wechat", "对公微信"),
                    ("alipay", "对公支付宝"),
                ],
                max_length=32,
                verbose_name="参会费支付方式",
            ),
        ),
        migrations.AlterField(
            model_name="clientstudent",
            name="education",
            field=models.CharField(
                choices=[
                    ("associate", "专科"),
                    ("bachelor", "本科"),
                    ("master", "硕士研究生"),
                    ("doctorate", "博士生"),
                ],
                max_length=32,
                verbose_name="学历",
            ),
        ),
        migrations.AlterField(
            model_name="coursetemplate",
            name="certification_body",
            field=models.JSONField(
                choices=[("miit_talent_center", "工信部人才中心"), ("exam_center", "教考中心")],
                default=list,
                verbose_name="认证机构",
            ),
        ),
        migrations.AlterField(
            model_name="coursetemplate",
            name="level",
            field=models.CharField(
                choices=[("primary", "初级"), ("intermediate", "中级"), ("senior", "高级")],
                max_length=32,
                verbose_name="级别",
            ),
        ),
    ]
