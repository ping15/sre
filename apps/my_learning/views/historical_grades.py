import random
from collections import defaultdict

from rest_framework.views import APIView

from apps.my_learning.serializers.historical_grades import (
    HistoricalGradesListSerializer,
)
from apps.platform_management.models import ClientStudent
from apps.teaching_space.models import TrainingClass
from common.utils.drf.permissions import StudentPermission
from common.utils.drf.response import Response
from exam_system.models import ExamStudent


class HistoricalGradesApiView(APIView):
    permission_classes = [StudentPermission]

    def get(self, request, *args, **kwargs):
        user: ClientStudent = self.request.user
        exam_students = ExamStudent.objects.filter(student_name=user.username, password=user.phone)

        union_training_class_grades = defaultdict(list)
        training_class_ids = set()
        for grade in HistoricalGradesListSerializer(exam_students, many=True).data:
            union_training_class_grades[grade["exam_info"]["training_class_id"]].append(grade)
            training_class_ids.add(grade["exam_info"].pop("training_class_id"))

        training_class_id_to_name = {tc.id: tc.name for tc in TrainingClass.objects.filter(id__in=training_class_ids)}

        return Response([
            {
                "training_class_name": training_class_id_to_name.get(training_class_id, ""),
                "grades": grades,
                "is_pass": random.choice([True, False]),
            }
            for training_class_id, grades in union_training_class_grades.items()
        ])
