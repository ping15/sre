import random
from collections import defaultdict
from typing import List

from django.db.models import QuerySet

from apps.teaching_space.serializers.training_class import TrainingCLassGradesSerializer


class ExamSystemTool:
    @staticmethod
    def build_exam_students(exam_students: QuerySet) -> List[dict]:
        union_student_grades = defaultdict(list)
        for grade in TrainingCLassGradesSerializer(exam_students, many=True).data:
            union_student_grades[f"{grade.pop('student_name')}(-|-|-){grade.pop('password')}"].append(grade)

        return [
            {
                "student_name": student_key.split("(-|-|-)")[0],
                "grades": grades,
                "score": 0,
                "is_pass": random.choice([True, False]),
            }
            for student_key, grades in union_student_grades.items()
        ]
