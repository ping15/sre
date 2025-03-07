from django.urls import include, path
from rest_framework import routers

from .views.administrator import AdministratorModelViewSet
from .views.all_classes import AllClassesModelViewSet
from .views.all_schedules import AllScheduleModelViewSet
from .views.attachment import FileUploadDownloadView
from .views.client_approval_slip import ClientApprovalSlipModelViewSet
from .views.client_company import ClientCompanyModelViewSet
from .views.client_student import ClientStudentModelViewSet
from .views.course_template import CourseTemplateModelViewSet
from .views.instructor import InstructorModelViewSet
from .views.management_company import ManagementCompanyModelViewSet

router = routers.SimpleRouter(trailing_slash=True)

# 客户资料审批
router.register(
    "client_approval_slip",
    ClientApprovalSlipModelViewSet,
    basename="client_approval_slip",
)

# 全部培训班
router.register("all_classes", AllClassesModelViewSet, basename="all_classes")

# 全部日程
router.register("all_schedule", AllScheduleModelViewSet, basename="all_schedule")

# 课程模板
router.register(r"course_template", CourseTemplateModelViewSet, basename="course_template")

# 讲师
router.register(r"instructor", InstructorModelViewSet, basename="instructor")

# 调查问卷模板

# 客户公司
router.register(r"client_company", ClientCompanyModelViewSet, basename="client_company")

# 客户学员
router.register(r"client_student", ClientStudentModelViewSet, basename="client_student")

# 管理公司
router.register(
    r"management_company", ManagementCompanyModelViewSet, basename="management_company"
)

# 管理员
router.register(r"administrator", AdministratorModelViewSet, basename="administrator")

urlpatterns = [
    path("", include(router.urls)),
    path("attachment/", FileUploadDownloadView.as_view(), name="file-upload-download"),
    # path("attachment/<int:pk>/", FileDownloadView.as_view(), name="file-download"),
]
