# Generated by Django 3.2.12 on 2024-09-19 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teaching_space', '0012_auto_20240918_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingclass',
            name='questionnaire_qr_code',
            field=models.JSONField(default=dict, verbose_name='问卷二维码'),
        ),
    ]