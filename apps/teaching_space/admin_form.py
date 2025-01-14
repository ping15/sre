from django import forms

from apps.teaching_space.models import TrainingClass


class TrainingClassModelForm(forms.ModelForm):
    """培训班"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 非必填字段
        self.fields["instructor"].required = False
        self.fields["questionnaire_qr_code"].required = False

        # 限定学员为该客户公司下的
        self.fields["client_students"].queryset = self.instance.target_client_company.students

    class Meta:
        model = TrainingClass
        fields = "__all__"
