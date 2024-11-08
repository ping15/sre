from django.core.management.base import BaseCommand

from apps.platform_management.models import Instructor


class Command(BaseCommand):
    help = "清洗已授课程"

    def handle(self, *args, **kwargs):
        instructors_to_update = []
        for instructor in Instructor.objects.all():
            teachable_courses = instructor.teachable_courses
            cleaned_courses = [course for course in teachable_courses if isinstance(course, int)]

            if cleaned_courses != teachable_courses:
                instructor.teachable_courses = cleaned_courses
                instructors_to_update.append(instructor)

        Instructor.objects.bulk_update(instructors_to_update, batch_size=500, fields=["teachable_courses"])
