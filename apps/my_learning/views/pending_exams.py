import datetime

from rest_framework.views import APIView

from apps.platform_management.models import ClientStudent
from common.utils.drf.permissions import StudentPermission
from common.utils.drf.response import Response
from exam_system.models import ExamArrange, ExamStudent


class PendingExamsApiView(APIView):
    permission_classes = [StudentPermission]

    def get(self, request, *args, **kwargs):
        user: ClientStudent = self.request.user
        exam_students = ExamStudent.objects.filter(student_name=user.exam_username, is_commit=0)
        pending_exam_count: int = 0
        now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

        # 【未提交】且【未到考试结束时间】的算一场待考试
        for exam in ExamArrange.objects.filter(id__in=exam_students.values_list("exam_id", flat=True)):
            pending_exam_count = pending_exam_count + 1 if exam.end_time > now else pending_exam_count

        return Response({"pending_exam_count": pending_exam_count})
