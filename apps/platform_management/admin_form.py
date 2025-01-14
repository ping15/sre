from django import forms

from apps.platform_management.models import Event


class CourseTemplateModelForm(forms.ModelForm):
    """课程模板"""


class ManageCompanyModelForm(forms.ModelForm):
    """管理公司"""


class AdministratorModelForm(forms.ModelForm):
    """管理员"""


class InstructorModelForm(forms.ModelForm):
    """讲师"""


class ClientCompanyModelForm(forms.ModelForm):
    """客户公司"""


class ClientStudentModelForm(forms.ModelForm):
    """客户学员"""


class ClientApprovalSlipModelForm(forms.ModelForm):
    """客户审批单据"""


class EventModelForm(forms.ModelForm):
    """日程事件"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 非必填字段
        self.fields["freq_interval"].required = False

    class Meta:
        model = Event
        fields = "__all__"
