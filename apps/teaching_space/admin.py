from django.contrib import admin

from apps.teaching_space.admin_form import *
from apps.teaching_space.models import TrainingClass


@admin.register(TrainingClass)
class TrainingClassModelAdmin(admin.ModelAdmin):
    """培训班"""

    list_display = ["id", "name", "status", "student_count", "instructor_name", "is_published"]
    list_filter = ["is_published", "status"]
    search_fields = ["id", "name", "status", "is_published"]
    exclude = ["creator"]
    form = TrainingClassModelForm

    @admin.display(description="名称")
    def name(self, obj: TrainingClass) -> str:
        return obj.name

    @admin.display(description="学员数量")
    def student_count(self, obj: TrainingClass) -> int:
        return obj.student_count

    @admin.display(description="讲师名称")
    def instructor_name(self, obj: TrainingClass) -> str:
        return obj.instructor_name
