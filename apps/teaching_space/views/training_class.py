from apps.teaching_space.models import TrainingClass
from apps.teaching_space.serializers.training_class import (
    TrainingClassListSerializer,
    TrainingClassCreateSerializer,
    TrainingClassRetrieveSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import ManageCompanyAdministratorPermission


class TrainingClassModelViewSet(ModelViewSet):
    permission_classes = [ManageCompanyAdministratorPermission]
    queryset = TrainingClass.objects.all()
    default_serializer_class = TrainingClassCreateSerializer
    ACTION_MAP = {
        "list": TrainingClassListSerializer,
        "create": TrainingClassCreateSerializer,
        "retrieve": TrainingClassRetrieveSerializer,
    }

    # def list(self, request, *args, **kwargs):
    #     mock_data = [
    #         {
    #             "name": "SRE 专家培训课(中级)-1期",
    #             "status": "筹备中",
    #             "student_count": "56",
    #             "instructor": "nekzhang",
    #         },
    #         {
    #             "name": "SRE 专家培训课(中级)-2期",
    #             "status": "开课中",
    #             "student_count": "42",
    #             "instructor": "nekzhang",
    #         },
    #     ]
    #     return Response(mock_data)

    # def retrieve(self, request, *args, **kwargs):
    #     mock_data = {
    #         "name": "SRE 专家培训课(中级)-2期",
    #         "status": "开课中",
    #         "class_mode": "线下课",
    #         "num_lessons": 12,
    #         "start_date": "2024-05-10",
    #         "assessment_method": "闭卷考试",
    #         "certification": "无证",
    #         "location": "广东省深圳市南山区科兴科学院D2栋",
    #     }
    #     return Response(mock_data)
