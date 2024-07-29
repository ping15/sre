from apps.teaching_space.models import TrainingClass
from apps.platform_management.serialiers.all_classes import AllClassesListSerializer
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class AllClassesModelViewSet(ModelViewSet):
    permission_classes = [SuperAdministratorPermission]
    queryset = TrainingClass.objects.all()
    fuzzy_filter_fields = ["target_client_company_name", "location"]
    property_fuzzy_filter_fields = [
        "name",
        "instructor_name",
        "affiliated_manage_company_name",
    ]
    time_filter_fields = ["start_date"]
    filter_condition_mapping = {
        "客户公司": "target_client_company_name",
        "管理公司": "affiliated_manage_company_name",
        "培训班名称": "name",
        "讲师": "instructor_name",
        "上课地点": "location",
    }
    ACTION_MAP = {
        "list": AllClassesListSerializer,
    }
