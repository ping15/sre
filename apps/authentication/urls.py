from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from apps.authentication.views import AuthenticationViewSet
from home_application import views

router = routers.DefaultRouter(trailing_slash=True)

router.register(r"", AuthenticationViewSet, basename="login")

urlpatterns = [
    url(r"^$", views.home),
    path("", include(router.urls)),
]
