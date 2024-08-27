from django.urls import include, path
from rest_framework import routers

from apps.my_lectures.views.advertisement import AdvertisementViewSet
from apps.my_lectures.views.instructor_event import InstructorEventModelViewSet
from apps.my_lectures.views.schedule import ScheduleModelViewSet

router = routers.DefaultRouter(trailing_slash=True)

router.register(r"schedule", ScheduleModelViewSet, basename="schedule")
router.register(r"instructor_event", InstructorEventModelViewSet, basename="instructor_event")
router.register(r"advertisement", AdvertisementViewSet, basename="advertisement")

urlpatterns = [
    path("", include(router.urls)),
]
