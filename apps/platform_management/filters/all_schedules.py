import django_filters
from django.db.models import QuerySet

from apps.platform_management.models import Event
from apps.teaching_space.models import TrainingClass
from common.utils.drf.filters import BaseFilterSet, NumberInFilter


class AllScheduleFilterClass(BaseFilterSet):
    manage_company = django_filters.NumberFilter(method="filter_manage_company")
    client_company = django_filters.NumberFilter("training_class__target_client_company_id", lookup_expr="exact")
    instructor = NumberInFilter(field_name="instructor_id")
    training_class = NumberInFilter(field_name="training_class_id")

    def filter_manage_company(self, queryset: QuerySet["Event"], name, value):
        Event.objects.filter(training_class__target_client_company__affiliated_manage_company_name__contains=1)
        return queryset.filter(
            training_class__in=TrainingClass.objects.filter(
                id__in=[
                    training_class.id
                    for training_class in TrainingClass.objects.all()
                    if training_class.affiliated_manage_company.id == value
                ]
            )
        )

    # def filter_client_company(self, queryset: QuerySet["Event"], name, value):
    #     return queryset.filter(
    #         training_class__in=TrainingClass.objects.filter(
    #             id__in=[
    #                 training_class.id
    #                 for training_class in TrainingClass.objects.all()
    #                 if training_class.target_client_company_id == value
    #             ]
    #         )
    #     )

    # def filter_instructor(self, queryset, name, value):
    #     return queryset.filter(instructor_id__in=value)
    #
    # def filter_train_class(self, queryset, name, value):
    #     return queryset.filter(trianing_class_id__in=value)

    class Meta:
        model = Event
        fields = ["manage_company", "client_company", "instructor", "training_class"]
