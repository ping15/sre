from django.contrib import admin

from apps.my_lectures.models import *


@admin.register(InstructorEvent)
class InstructorEventModelAdmin(admin.ModelAdmin):
    list_display = ["id", "event_name", "event_type", "initiator", "status", "created_datetime"]
    list_filter = ["event_type", "status"]
    search_fields = list_display


@admin.register(Advertisement)
class AdvertisementModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "training_class",
        "enrolment_count",
        "deadline_datetime",
        "location",
        "is_revoked",
    ]
    list_filter = ["is_revoked"]
    search_fields = ["id", "enrolment_count", "deadline_datetime", "location", "is_revoked"]


@admin.register(InstructorEnrolment)
class InstructorEnrolmentModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "instructor",
        "advertisement",
        "status",
    ]
    list_filter = ["status"]
    search_fields = ["id", "status"]
