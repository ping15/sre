from django.contrib import admin

from apps.teaching_space.models import *


@admin.register(TrainingClass)
class TrainingClassModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "status", "student_count", "instructor_name", "is_published"]
    list_filter = ["is_published", "status"]
    search_fields = ["id", "name", "status", "is_published"]
