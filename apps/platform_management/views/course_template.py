from django_filters.rest_framework import DjangoFilterBackend

from apps.platform_management.filters.course_templates import (
    CourseTemplateFilterClass,
    CourseTemplateOrderingFilter,
)
from apps.platform_management.models import CourseTemplate
from apps.platform_management.serialiers.course_template import (
    CourseTemplateCreateSerializer,
    CourseTemplateListSerializer,
)
from common.utils.modelviewset import ModelViewSet
from common.utils.permissions import SuperAdministratorPermission


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
