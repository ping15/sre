import django_filters
from django.core.exceptions import ObjectDoesNotExist

from apps.platform_management.models import ManageCompany, ClientCompany, Instructor
from apps.teaching_space.models import TrainingClass
from common.utils.drf.filters import BaseFilterSet


class AllScheduleFilterClass(BaseFilterSet):
    manage_company = django_filters.NumberFilter(method="filter_manage_company")
    client_company = django_filters.NumberFilter(method="filter_client_company")
    instructor = django_filters.NumberFilter(method="filter_instructor")
    train_class = django_filters.NumberFilter(method="filter_train_class")

    def filter_manage_company(self, queryset, name, value):
        return self._filter_by_related_model(
            queryset, value, ManageCompany, "affiliated_manage_company_name", "name"
        )

    def filter_client_company(self, queryset, name, value):
        return self._filter_by_related_model(
            queryset, value, ClientCompany, "target_client_company_name", "name"
        )

    def filter_instructor(self, queryset, name, value):
        return self._filter_by_related_model(
            queryset, value, Instructor, "instructor_name", "username"
        )

    def filter_train_class(self, queryset, name, value):
        return self._filter_by_related_model(
            queryset, value, TrainingClass, "name", "name"
        )

    class Meta:
        model = TrainingClass
        fields = ["manage_company", "client_company", "instructor", "train_class"]
