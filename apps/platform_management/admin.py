from django.contrib import admin

from apps.platform_management.admin_form import *
from apps.platform_management.models import *


@admin.register(CourseTemplate)
class CourseTemplateModelAdmin(admin.ModelAdmin):
    """课程模板"""

    list_display = [
        "id",
        "name",
        "level",
        "num_lessons",
        "status",
    ]
    search_fields = list_display
    form = CourseTemplateModelForm


@admin.register(ManageCompany)
class ManageCompanyModelAdmin(admin.ModelAdmin):
    """管理公司"""

    list_display = ["id", "name", "type", "email"]
    list_filter = ["type"]
    search_fields = list_display
    form = ManageCompanyModelForm


@admin.register(Administrator)
class AdministratorModelAdmin(admin.ModelAdmin):
    """管理员"""

    list_display = ["id", "username", "phone", "email", "affiliated_manage_company", "role"]
    search_fields = ["username", "phone"]
    form = AdministratorModelForm


@admin.register(Instructor)
class InstructorModelAdmin(admin.ModelAdmin):
    """讲师"""

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
    form = InstructorModelForm


@admin.register(ClientCompany)
class ClientCompanyModelAdmin(admin.ModelAdmin):
    """客户公司"""

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
    form = ClientCompanyModelForm

    @admin.display(description="学员数量")
    def student_count(self, obj):
        return obj.student_count


@admin.register(ClientStudent)
class ClientStudentModelAdmin(admin.ModelAdmin):
    """客户学员"""

    list_display = ["id", "username", "gender", "id_number", "education", "email", "affiliated_client_company_name"]
    list_filter = ["gender", "education"]
    search_fields = list_display
    form = ClientStudentModelForm


@admin.register(ClientApprovalSlip)
class ClientApprovalSlipModelAdmin(admin.ModelAdmin):
    """客户审批单据"""

    list_display = [
        "id",
        "name",
        "affiliated_manage_company_name",
        "affiliated_client_company_name",
        "submitter",
        "status",
        "formatted_submission_datetime",
    ]
    list_filter = ["status"]
    search_fields = list_display
    form = ClientApprovalSlipModelForm

    @admin.display(description="提单时间", ordering="submission_datetime")
    def formatted_submission_datetime(self, obj: ClientApprovalSlip):
        return obj.submission_datetime.strftime("%Y年%m月%d日 %H:%M")


@admin.register(Event)
class EventModelAdmin(admin.ModelAdmin):
    """日程事件"""

    list_display = [
        "id",
        "event_type",
        "freq_type",
        "freq_interval",
        "formatted_start_date",
        "formatted_end_date",
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
    formfield_overrides = {
        models.DateField: {'widget': forms.DateInput(attrs={'type': 'date'})},
    }
    form = EventModelForm

    @admin.display(description="开始时间", ordering="start_date")
    def formatted_start_date(self, obj: Event):
        return obj.start_date.strftime("%Y年%m月%d日")

    @admin.display(description="结束时间", ordering="end_date")
    def formatted_end_date(self, obj: Event):
        return obj.end_date.strftime("%Y年%m月%d日") if obj.end_date else None
