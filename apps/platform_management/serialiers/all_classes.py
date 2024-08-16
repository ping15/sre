from rest_framework import serializers

from apps.teaching_space.models import TrainingClass


class AllClassesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = [
            "id",
            "start_date",
            "name",
            "target_client_company_name",
            "instructor_name",
            "location",
            "affiliated_manage_company_name",
        ]
