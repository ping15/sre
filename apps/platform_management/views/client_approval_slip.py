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
    integer_filter_fields = ["id"]
    fuzzy_filter_fields = [
        "affiliated_manage_company_name",
        "affiliated_client_company_name",
        "submitter",
        "status",
    ]
    datetime_filter_fields = ["submission_datetime"]
    filter_condition_mapping = {
        "审批单号": "id",
        "管理公司": "affiliated_manage_company_name",
        "客户公司": "affiliated_client_company_name",
        "提单人": "submitter",
        "审批状态": "status",
        "时间": "submission_datetime",
    }
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
