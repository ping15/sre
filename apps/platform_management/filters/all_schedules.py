import django_filters
from django.core.exceptions import ObjectDoesNotExist

from apps.platform_management.models import ManageCompany, ClientCompany, Instructor
from apps.teaching_space.models import TrainingClass
from common.utils.drf.filters import PropertyFilter


class AllScheduleFilterClass(django_filters.FilterSet):
    manage_company = django_filters.NumberFilter(method="filter_manage_company")
    client_company = django_filters.NumberFilter(method="filter_client_company")
    instructor = django_filters.NumberFilter(method="filter_instructor")
    train_class = django_filters.NumberFilter(method="filter_train_class")

    def filter_manage_company(self, queryset, name, value):
        try:
            return PropertyFilter("affiliated_manage_company_name").filter(
                queryset, ManageCompany.objects.get(id__in=value).name
            )
        except ObjectDoesNotExist:
            return queryset.none()

    def filter_client_company(self, queryset, name, value):
        try:
            return queryset.filter(
                target_client_company_name=ClientCompany.objects.get(id__in=value).name
            )
        except ObjectDoesNotExist:
            return queryset.none()

    def filter_instructor(self, queryset, name, value):
        try:
            return PropertyFilter("instructor_name").filter(
                queryset, Instructor.objects.get(id=value).name
            )
        except ObjectDoesNotExist:
            return queryset.none()

    def filter_train_class(self, queryset, name, value):
        try:
            return PropertyFilter("name").filter(
                queryset, TrainingClass.objects.get(id__in=value).name
            )
        except ObjectDoesNotExist:
            return queryset.none()

    class Meta:
        model = TrainingClass
        fields = ["manage_company", "client_company", "instructor", "train_class"]
