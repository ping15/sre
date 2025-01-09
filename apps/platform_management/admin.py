from django.contrib import admin

from apps.platform_management.models import *


def add_description(description=""):
    def decorator(func):
        func.short_description = description
        return func
    return decorator


class BaseModelAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseTemplate)
class CourseTemplateModelAdmin(BaseModelAdmin):
    list_display = [
        "id",
        "name",
        "level",
        "num_lessons",
        "status",
    ]
    search_fields = list_display


@admin.register(ManageCompany)
class ManageCompanyModelAdmin(BaseModelAdmin):
    list_display = ["id", "name", "type", "email"]
    list_filter = ["type"]
    search_fields = list_display


@admin.register(Administrator)
class AdministratorModelAdmin(BaseModelAdmin):
    list_display = ["id", "username", "phone", "email", "affiliated_manage_company", "role"]
    search_fields = ["username", "phone"]


@admin.register(Instructor)
class InstructorModelAdmin(BaseModelAdmin):
    """"""
    list_display = [
        "id",
        "username",
        "email",
        "phone",
        "hours_taught",
        "satisfaction_score",
        "is_partnered",
        "introduction",
        "city",
    ]
    search_fields = list_display


@admin.register(ClientCompany)
class ClientCompanyModelAdmin(BaseModelAdmin):
    """"""
    list_display = [
        "id",
        "name",
        "contact_email",
        "contact_phone",
        "contact_person",
        "affiliated_manage_company_name",
        "student_count"
    ]
    search_fields = [
        "id",
        "name",
        "contact_email",
        "contact_phone",
        "contact_person",
        "affiliated_manage_company_name",
    ]

    @add_description(description="学员数")
    def student_count(self, obj):
        return obj.student_count


@admin.register(ClientStudent)
class ClientStudentModelAdmin(BaseModelAdmin):
    list_display = ["id", "username", "gender", "id_number", "education", "email", "affiliated_client_company_name"]
    list_filter = ["gender", "education"]
    search_fields = list_display


@admin.register(ClientApprovalSlip)
class ClientApprovalSlipModelAdmin(BaseModelAdmin):
    list_display = [
        "id",
        "name",
        "affiliated_manage_company_name",
        "affiliated_client_company_name",
        "submitter",
        "status",
        "submission_datetime",
    ]
    list_filter = ["status"]
    search_fields = list_display


@admin.register(Event)
class EventModelAdmin(BaseModelAdmin):
    """"""
    list_display = [
        "id",
        "event_type",
        "freq_type",
        "freq_interval",
        "start_date",
        "end_date",
        "instructor",
        "training_class",
    ]
    list_filter = ["event_type", "freq_type"]
    search_fields = [
        "id",
        "event_type",
        "freq_type",
        "freq_interval",
        "start_date",
        "end_date",
    ]

    def start_date(self, obj):
        return obj.start_date.strftime("%Y年%m月%d日")
    start_date.short_description = "xxxx"
