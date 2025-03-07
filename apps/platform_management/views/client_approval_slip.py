from django.db import transaction
from rest_framework.decorators import action

from apps.platform_management.filters.client_approval_slip import (
    ClientApprovalSlipFilterClass,
)
from apps.platform_management.models import ClientApprovalSlip
from apps.platform_management.serialiers.client_approval_slip import (
    ClientApprovalSlipCreateSerializer,
    ClientApprovalSlipListSerializer,
    ClientApprovalSlipPartialUpdateSerializer,
)
from apps.platform_management.serialiers.client_company import (
    ClientCompanyCreateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response


class ClientApprovalSlipModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = ClientApprovalSlip.objects.all()
    serializer_class = ClientApprovalSlipCreateSerializer
    filter_class = ClientApprovalSlipFilterClass
    ACTION_MAP = {
        "list": ClientApprovalSlipListSerializer,
        "create": ClientApprovalSlipCreateSerializer,
        "partial_update": ClientApprovalSlipPartialUpdateSerializer,
    }
    PERMISSION_MAP = {
        "create": [SuperAdministratorPermission | ManageCompanyAdministratorPermission],
    }

    def partial_update(self, request, *args, **kwargs):
        validated_data = self.validated_data

        instance: ClientApprovalSlip = self.get_object()
        if instance.status != ClientApprovalSlip.Status.PENDING.value:
            return Response(result=False, err_msg="该单据装填已流转，不可更新")

        with transaction.atomic():
            if validated_data["status"] == ClientApprovalSlip.Status.AGREED.value:
                # 创建客户公司
                create_serializer = ClientCompanyCreateSerializer(data=instance.submission_info)
                if not create_serializer.is_valid():
                    return Response(result=False, err_msg=str(create_serializer.errors))
                create_serializer.save()

            # 更新单据状态
            super().partial_update(request, *args, **kwargs)

        return Response()

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "id", "name": "审批单号", "children": []},
                {
                    "id": "affiliated_manage_company_name",
                    "name": "管理公司",
                    "children": [],
                },
                {
                    "id": "affiliated_client_company_name",
                    "name": "客户公司",
                    "children": [],
                },
                {"id": "submitter", "name": "提单人", "children": []},
                {"id": "status", "name": "审批状态", "children": [
                    {"id": choice.value, "name": choice.label}  # noqa
                    for choice in ClientApprovalSlip.Status
                ]},
            ]
        )
