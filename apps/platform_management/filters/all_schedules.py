import django_filters
from django.core.exceptions import ObjectDoesNotExist

from apps.platform_management.models import ManageCompany, ClientCompany, Instructor
from apps.teaching_space.models import TrainingClass


class AllScheduleFilterClass(django_filters.FilterSet):
    manage_company = django_filters.NumberFilter(method="filter_manage_company")
    client_company = django_filters.NumberFilter(method="filter_client_company")
    instructor = django_filters.NumberFilter(method="filter_instructor")
    train_class = django_filters.NumberFilter(method="filter_train_class")

    def _filter_by_related_model(
        self, queryset, value, model, field_name, related_field
    ):
        try:
            related_instance = model.objects.get(id=value)
            filter_value = getattr(related_instance, related_field)
            return queryset.filter(**{field_name: filter_value})
        except ObjectDoesNotExist:
            return queryset.none()

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
