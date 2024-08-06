from django_filters.rest_framework import DjangoFilterBackend

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
    # filter_backends = [DjangoFilterBackend]
    fuzzy_filter_fields = ["name", "course_overview"]
    permission_classes = [SuperAdministratorPermission]
    filter_condition_mapping = {
        "课程名称": "name",
        "课程描述": "course_overview",
    }
    ACTION_MAP = {
        "list": CourseTemplateListSerializer,
        "create": CourseTemplateCreateSerializer,
    }
