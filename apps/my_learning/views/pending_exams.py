from rest_framework.views import APIView

from apps.platform_management.models import ClientStudent

# from common.utils.drf.permissions import StudentPermission
from common.utils.drf.response import Response
from exam_system.models import ExamStudent


class PendingExamsApiView(APIView):
    # permission_classes = [StudentPermission]

    def get(self, request, *args, **kwargs):
        user: ClientStudent = self.request.user
        return Response({
            "pending_exam_count": ExamStudent.objects.filter(
                student_name=user.username, password=user.phone, is_commit=0).count()
        })
