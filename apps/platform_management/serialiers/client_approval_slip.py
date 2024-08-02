import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.platform_management.models import (
    ClientApprovalSlip,
    ManageCompany,
    ClientCompany,
)
from apps.platform_management.serialiers.client_company import (
    ClientCompanyCreateSerializer,
)


class ClientApprovalSlipListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientApprovalSlip
        exclude = ["submission_info"]


class ClientApprovalSlipCreateSerializer(serializers.ModelSerializer):
    submission_info = ClientCompanyCreateSerializer()

    def create(self, validated_data):
        request = self.context.get("request")
        submission_info = validated_data["submission_info"]

        if ClientApprovalSlip.objects.filter(
            affiliated_client_company_name=submission_info["name"]
        ).exists():
            raise ValidationError("该公司已申请")

        validated_data["affiliated_manage_company_name"] = submission_info[
            "affiliated_manage_company_name"
        ]
        validated_data["affiliated_client_company_name"] = submission_info["name"]
        validated_data["submitter"] = request.user.username
        validated_data["submission_datetime"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        validated_data[
            "name"
        ] = f"{submission_info['affiliated_manage_company_name']}申请给{submission_info['name']}培训服务"
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


class ClientApprovalSlipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientApprovalSlip
        fields = ["status"]


class ClientApprovalSlipPartialUpdateSerializer(serializers.ModelSerializer):
    # class ClientApprovalStatusSerializer(serializers.Serializer):
    #     status = serializers.CharField()
    #
    # submission_info = ClientApprovalStatusSerializer()
    class Meta:
        model = ClientApprovalSlip
        fields = ["status"]