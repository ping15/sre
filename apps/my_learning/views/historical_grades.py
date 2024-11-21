import random
from collections import defaultdict
from datetime import datetime
from typing import List

from django.http import QueryDict
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from apps.my_learning.serializers.historical_grades import (
    HistoricalGradesListSerializer,
)
from apps.platform_management.models import ClientStudent
from apps.teaching_space.models import TrainingClass
from common.utils.drf.permissions import StudentPermission
from common.utils.drf.response import Response
from exam_system.models import ExamStudent


class HistoricalGradesApiView(GenericViewSet):
    permission_classes = [StudentPermission]
    queryset = ExamStudent.objects.all()

    # region 列表
    def list(self, request, *args, **kwargs):
        user: ClientStudent = self.request.user

        # 当前考生所有已考过的历史成绩
        exam_students = ExamStudent.objects.filter(student_name=user.username, password=user.phone, is_commit=1)

        # 培训班id相同的聚合在一起
        training_class_id_to_grades, training_class_ids = defaultdict(list), set()
        for grade in HistoricalGradesListSerializer(exam_students, many=True).data:
            training_class_id_to_grades[grade["exam_info"]["training_class_id"]].append(grade)
            training_class_ids.add(grade["exam_info"].pop("training_class_id"))

        training_class_id_to_name = {tc.id: tc.name for tc in TrainingClass.objects.filter(id__in=training_class_ids)}

        # 添加额外数据并组装
        grade_infos: List[dict] = [
            {
                "training_class_name": training_class_id_to_name.get(training_class_id, ""),
                "grades": grades,
                "is_pass": random.choice([True, False, None]),
            }
            for training_class_id, grades in training_class_id_to_grades.items()
        ]

        # 筛选
        grade_infos = self._filter_grades(grade_infos, request.query_params)

        return self.get_paginated_response(self.paginate_queryset(grade_infos))

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response([
            {"id": "training_class_name", "name": "培训班名称", "children": []},
            {"id": "exam_title", "name": "考试名称", "children": []},
        ])
    # endregion

    # region 私有函数
    @staticmethod
    def _filter_grades(grade_infos: List[dict], query_params: QueryDict) -> List[dict]:
        """筛选学员成绩"""

        training_class_name = query_params.get("training_class_name")
        exam_title = query_params.get("exam_title")
        start_datetime_before = query_params.get("start_datetime_before")
        start_datetime_after = query_params.get("start_datetime_after")

        if not any([training_class_name, exam_title, start_datetime_before, start_datetime_after]):
            return grade_infos

        filtered_grades = []
        for grade_info in grade_infos:
            # 筛选培训班名称
            if training_class_name and training_class_name in grade_info["training_class_name"]:
                filtered_grades.append(grade_info)
                continue

            # 只要有一个符合则整个展示
            for grade_detail in grade_info["grades"]:
                # 筛选考试名称
                if exam_title and exam_title in grade_detail["exam_info"]["title"]:
                    filtered_grades.append(grade_info)
                    continue

                # 筛选开考时间
                start_time: str = grade_detail["start_time"]
                if start_time and start_datetime_after and start_datetime_before:
                    if datetime.fromisoformat(start_datetime_after) <= datetime.fromisoformat(start_time) \
                            <= datetime.fromisoformat(start_datetime_before):
                        filtered_grades.append(grade_info)
                        continue

        return filtered_grades
    # endregion
