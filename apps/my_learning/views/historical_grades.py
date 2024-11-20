from rest_framework.views import APIView

# from apps.platform_management.models import ClientStudent
from common.utils.drf.response import Response

# from exam_system.models import ExamStudent


class HistoricalGradesApiView(APIView):
    def get(self, request, *args, **kwargs):
        # user: ClientStudent = self.request.user
        # exam_students: ExamStudent = ExamStudent.objects.filter(student_name=user.username, password=user.phone)
        return Response()
