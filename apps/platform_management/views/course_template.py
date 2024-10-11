from django.db.models import Q
from rest_framework.decorators import action

from apps.platform_management.filters.course_templates import CourseTemplatesFilterClass
from apps.platform_management.models import CourseTemplate
from apps.platform_management.serialiers.course_template import (
    CourseTemplateCreateSerializer,
    CourseTemplateListSerializer,
    CourseTemplateUpdateSerializer,
)
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import (
    InstructorPermission,
    ManageCompanyAdministratorPermission,
    SuperAdministratorPermission,
)
from common.utils.drf.response import Response


class CourseTemplateModelViewSet(ModelViewSet):
    queryset = CourseTemplate.objects.all()
    serializer_class = CourseTemplateCreateSerializer
    filter_class = CourseTemplatesFilterClass
    permission_classes = [SuperAdministratorPermission]
    ACTION_MAP = {
        "list": CourseTemplateListSerializer,
        "create": CourseTemplateCreateSerializer,
        "update": CourseTemplateUpdateSerializer,
    }

    def destroy(self, request, *args, **kwargs):
        course_template: CourseTemplate = self.get_object()
        if course_template.status != CourseTemplate.Status.TERMINATED:
            return Response(result=False, err_msg="非[停课]状态课程不可删除")

        return super().destroy(request, *args, **kwargs)

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        return Response(
            [
                {"id": "name", "name": "课程名称", "children": []},
                {"id": "course_overview", "name": "课程描述", "children": []},
            ]
        )

    @action(methods=["GET"], detail=False, permission_classes=[
        SuperAdministratorPermission | ManageCompanyAdministratorPermission | InstructorPermission
    ])
    def choices(self, request, *args, **kwargs):
        return Response([
            {"id": course_template.id, "name": course_template.name}
            for course_template in self.get_queryset().filter(
                Q(status=CourseTemplate.Status.IN_PROGRESS.value) | Q(
                    status=CourseTemplate.Status.PREPARATION.value)
            )
        ])
