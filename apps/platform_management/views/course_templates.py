from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet

from apps.platform_management.filters.course_templates import CourseTemplateFilterClass, CourseTemplateOrderingFilter
from apps.platform_management.models import CourseTemplate
from apps.platform_management.serialiers.course_templates import (
    CourseTemplateCreateSerializer,
    CourseTemplateListSerializer
)
from common.permissions import SuperAdministratorPermission


class CourseTemplateModelViewSet(ModelViewSet):
    queryset = CourseTemplate.objects.all()
    serializer_class = CourseTemplateListSerializer
    filter_backends = [DjangoFilterBackend, CourseTemplateOrderingFilter]
    filter_class = CourseTemplateFilterClass
    permission_classes = [SuperAdministratorPermission]

    ACTION_MAP = {
        "list": CourseTemplateListSerializer,
        "create": CourseTemplateCreateSerializer,
    }

    def get_serializer_class(self):
        return self.ACTION_MAP.get(self.action, self.serializer_class) # noqa
