from django.urls import include, path
from rest_framework import routers

from apps.authentication.views import AuthenticationViewSet

router = routers.DefaultRouter(trailing_slash=True)

router.register(r"", AuthenticationViewSet, basename="login")

urlpatterns = [
    path("", include(router.urls)),
]
