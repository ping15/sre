from django.urls import path, include
from rest_framework import routers

from .views.administrator import AdministratorModelViewSet
from .views.course_template import CourseTemplateModelViewSet
from .views.attachment import FileUploadView, FileDownloadView
from .views.instructor import InstructorModelViewSet
from .views.management_company import ManagementCompanyModelViewSet

router = routers.DefaultRouter(trailing_slash=True)

# 客户资料审批

# 全部课程

# 全部日程

# 课程模板
router.register(
    r"course_template", CourseTemplateModelViewSet, basename="course_template"
)

# 讲师
router.register(r"instructor", InstructorModelViewSet, basename="instructor")

# 调查问卷模板

# 客户公司

# 客户学员

# 管理公司
router.register(
    r"management_company", ManagementCompanyModelViewSet, basename="management_company"
)

# 管理员
router.register(r"administrator", AdministratorModelViewSet, basename="administrator")

urlpatterns = [
    path("", include(router.urls)),
    path("attachment/", FileUploadView.as_view(), name="file-upload"),
    path("attachment/<int:pk>/", FileDownloadView.as_view(), name="file-download"),
]
