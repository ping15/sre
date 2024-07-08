from django.urls import path, include
from rest_framework import routers

from .views.administrators import AdministratorModelViewSet
from .views.course_templates import CourseTemplateModelViewSet
from .views.attachment import FileUploadView, FileDownloadView

router = routers.DefaultRouter(trailing_slash=True)

# 客户资料审批

# 全部课程

# 全部日程

# 课程模板
router.register(r"course_template", CourseTemplateModelViewSet, basename="course_template")

# 讲师

# 调查问卷模板

# 客户公司

# 客户学员

# 管理公司

# 管理员
router.register(r"administrator", AdministratorModelViewSet, basename="administrator")

urlpatterns = [
    path('', include(router.urls)),
    path('attachment/', FileUploadView.as_view(), name='file-upload'),
    path('attachment/<int:pk>/', FileDownloadView.as_view(), name='file-download'),
]
