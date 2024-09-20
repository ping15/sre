from django.urls import include, path
from rest_framework import routers

from apps.my_lectures.views.advertisement import AdvertisementViewSet
from apps.my_lectures.views.base_info import BaseInfoApiView
from apps.my_lectures.views.instructor_event import InstructorEventModelViewSet
from apps.my_lectures.views.my_training_class import MyTrainingClassViewSet
from apps.my_lectures.views.schedule import ScheduleModelViewSet

router = routers.DefaultRouter(trailing_slash=True)

# 日程
router.register(r"schedule", ScheduleModelViewSet, basename="schedule")

# 讲师报名
router.register(r"instructor_event", InstructorEventModelViewSet, basename="instructor_event")

# 广告信息
router.register(r"advertisement", AdvertisementViewSet, basename="advertisement")

# 我的课程
router.register(r"my_training_class", MyTrainingClassViewSet, basename="my_training_class")

urlpatterns = [
    path("", include(router.urls)),

    # 基本信息
    path('base_info/', BaseInfoApiView.as_view(), name='base_info'),
]
