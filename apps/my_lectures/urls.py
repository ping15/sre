from django.urls import path, include
from rest_framework import routers

from apps.my_lectures.views.event import EventModelViewSet

router = routers.DefaultRouter(trailing_slash=True)

router.register(r"event", EventModelViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
]
