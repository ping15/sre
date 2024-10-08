# Generated by Django 3.2.12 on 2024-08-28 03:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teaching_space', '0008_trainingclass_publish_type'),
        ('my_lectures', '0003_alter_instructorevent_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructorevent',
            name='training_class',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='instructor_event', to='teaching_space.trainingclass', verbose_name='培训班'),
        ),
    ]
