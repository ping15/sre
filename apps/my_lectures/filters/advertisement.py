import django_filters
from django.db.models import QuerySet

from apps.my_lectures.models import Advertisement, InstructorEnrolment
from common.utils.drf.filters import BaseFilterSet


class AdvertisementFilterClass(BaseFilterSet):
    course_name = django_filters.CharFilter("training_class", "course__name__icontains")
    position = django_filters.CharFilter("location", "icontains")
    course_level = django_filters.CharFilter("training_class", "course__level__exact")
    deadline_datetime = django_filters.DateTimeFromToRangeFilter("deadline_datetime")
    status = django_filters.CharFilter(method="filter_status")

    def filter_status(self, queryset: QuerySet["Advertisement"], name: str, status: str):
        instructor_enrolments: QuerySet["InstructorEnrolment"] = InstructorEnrolment.objects. \
            filter(instructor=self.request.user, status__in=status.split(","))

        return queryset.filter(id__in=instructor_enrolments.values_list('advertisement_id', flat=True))
