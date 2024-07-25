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
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission


class CourseTemplateModelViewSet(ModelViewSet):
    queryset = CourseTemplate.objects.all()
    default_serializer_class = CourseTemplateCreateSerializer
    filter_backends = [DjangoFilterBackend, CourseTemplateOrderingFilter]
    fuzzy_filter_fields = ["name", "course_overview"]
    permission_classes = [SuperAdministratorPermission]
    ACTION_MAP = {
        "list": CourseTemplateListSerializer,
        "create": CourseTemplateCreateSerializer,
    }
