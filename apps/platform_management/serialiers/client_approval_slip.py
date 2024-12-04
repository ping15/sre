import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.platform_management.models import (
    Administrator,
    ClientApprovalSlip,
    ClientCompany,
)
from apps.platform_management.serialiers.client_company import (
    ClientCompanyCreateSerializer,
)
from common.utils.drf.serializer_fields import ChoiceField


class ClientApprovalSlipListSerializer(serializers.ModelSerializer):
    submission_datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ClientApprovalSlip
        exclude = ["submission_info"]


class ClientApprovalSlipCreateSerializer(serializers.ModelSerializer):
    submission_info = ClientCompanyCreateSerializer(label="客户公司申请信息")

    def to_internal_value(self, data):
        if ClientCompany.objects.filter(name=data.get("name", "")).exists():
            raise ValidationError({"name": "该客户公司已存在"})

        return super().to_internal_value({"submission_info": data, "status": ClientApprovalSlip.Status.PENDING})

    def create(self, validated_data):
        request = self.context.get("request")
        submission_info = validated_data["submission_info"]

        user: Administrator = request.user
        if not user.is_super_administrator and user.affiliated_manage_company_name != \
                submission_info["affiliated_manage_company_name"]:
            raise ValidationError("鸿雪/合作伙伴管理员不可为其他管理公司申请客户公司")

        if ClientApprovalSlip.objects.filter(affiliated_client_company_name=submission_info["name"]).exists():
            raise ValidationError("该公司已申请")

        validated_data["affiliated_manage_company_name"] = submission_info["affiliated_manage_company_name"]
        validated_data["affiliated_client_company_name"] = submission_info["name"]
        validated_data["submitter"] = user.username
        validated_data["submission_datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        validated_data["name"] = (f"{submission_info['affiliated_manage_company_name']}申请"
                                  f"给{submission_info['name']}培训服务")
        return super().create(validated_data)

    class Meta:
        model = ClientApprovalSlip
        fields = "__all__"
        read_only_fields = [
            "submitter",
            "submission_datetime",
            "name",
            "affiliated_manage_company_name",
            "affiliated_client_company_name",
        ]


class ClientApprovalSlipPartialUpdateSerializer(serializers.ModelSerializer):
    status = ChoiceField(choices=ClientApprovalSlip.Status.choices)

    class Meta:
        model = ClientApprovalSlip
        fields = ["status"]
