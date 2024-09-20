from rest_framework import serializers

from apps.teaching_space.models import TrainingClass


class MyTrainingClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = ["id", "start_date", "name", "target_client_company_name", "location"]


class MyTrainingClassRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingClass
        fields = ["name", "questionnaire_qr_code"]
