from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from apps.platform_management.filters.course_templates import CourseTemplatesFilterClass
from apps.platform_management.models import CourseTemplate
from apps.platform_management.serialiers.course_template import (
    CourseTemplateCreateSerializer,
    CourseTemplateListSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import SuperAdministratorPermission
from common.utils.drf.response import Response


class CourseTemplateModelViewSet(ModelViewSet):
    queryset = CourseTemplate.objects.all()
    serializer_class = CourseTemplateCreateSerializer
    filter_class = CourseTemplatesFilterClass
    permission_classes = [SuperAdministratorPermission]
    ACTION_MAP = {
        "list": CourseTemplateListSerializer,
        "create": CourseTemplateCreateSerializer,
    }

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "name", "name": "课程名称", "children": []},
                {"id": "course_overview", "name": "课程描述", "children": []},
            ]
        )
