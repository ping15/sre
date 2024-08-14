from rest_framework.decorators import action

from apps.platform_management.filters.client_approval_slip import (
    ClientApprovalSlipFilterClass,
)
from apps.platform_management.models import ClientApprovalSlip
from apps.platform_management.serialiers.client_approval_slip import (
    ClientApprovalSlipListSerializer,
    ClientApprovalSlipCreateSerializer,
    ClientApprovalSlipPartialUpdateSerializer,
)
from apps.platform_management.serialiers.client_company import (
    ClientCompanyCreateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response


class ClientApprovalSlipModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = ClientApprovalSlip.objects.all()
    default_serializer_class = ClientApprovalSlipCreateSerializer
    # integer_filter_fields = ["id"]
    # string_fuzzy_filter_fields = [
    #     "affiliated_manage_company_name",
    #     "affiliated_client_company_name",
    #     "submitter",
    #     "status",
    # ]
    # datetime_filter_fields = ["submission_datetime"]
    filter_class = ClientApprovalSlipFilterClass
    ACTION_MAP = {
        "list": ClientApprovalSlipListSerializer,
        "create": ClientApprovalSlipCreateSerializer,
        "partial_update": ClientApprovalSlipPartialUpdateSerializer,
    }

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)

        instance: ClientApprovalSlip = self.get_object()
        if instance.status == ClientApprovalSlip.Status.APPROVED:
            create_serializer = ClientCompanyCreateSerializer(
                data=instance.submission_info
            )
            if not create_serializer.is_valid():
                return Response(result=False, err_msg=str(create_serializer.errors))

            create_serializer.save()

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
                {"id": "status", "name": "审批状态", "children": []},
                {"id": "submission_datetime", "name": "时间", "children": []},
            ]
        )
