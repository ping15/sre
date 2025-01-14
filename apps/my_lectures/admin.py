from django.contrib import admin

from apps.my_lectures.admin_form import *
from apps.my_lectures.models import *


@admin.register(InstructorEvent)
class InstructorEventModelAdmin(admin.ModelAdmin):
    """讲师事项"""

    list_display = ["id", "event_name", "event_type", "initiator", "status", "formatted_created_datetime"]
    list_filter = ["event_type", "status"]
    search_fields = list_display
    form = InstructorEventModelForm

    @admin.display(description="发起时间", ordering="created_datetime")
    def formatted_created_datetime(self, obj: InstructorEvent) -> str:
        return obj.created_datetime.strftime("%Y年%m月%d日")


@admin.register(Advertisement)
class AdvertisementModelAdmin(admin.ModelAdmin):
    """广告"""

    list_display = [
        "id",
        "training_class",
        "enrolment_count",
        "formatted_deadline_datetime",
        "location",
        "is_revoked",
    ]
    list_filter = ["is_revoked"]
    search_fields = ["id", "enrolment_count", "deadline_datetime", "location", "is_revoked"]
    form = AdvertisementModelForm

    @admin.display(description="截止时间", ordering="deadline_datetime")
    def formatted_deadline_datetime(self, obj: Advertisement) -> str:
        return obj.deadline_datetime.strftime("%Y年%m月%d日 %H:%M")


@admin.register(InstructorEnrolment)
class InstructorEnrolmentModelAdmin(admin.ModelAdmin):
    """报名状况"""

    list_display = [
        "id",
        "instructor",
        "advertisement",
        "status",
    ]
    list_filter = ["status"]
    search_fields = ["id", "status"]
    form = InstructorEnrolmentModelForm
