from rest_framework import serializers

from apps.platform_management.models import Instructor
from common.utils.drf.serializer_fields import ChoiceField
from common.utils.drf.serializer_validator import (
    BasicSerializerValidator,
    PhoneCreateSerializerValidator,
)
from common.utils.global_constants import AppModule


class InstructorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "hours_taught",
            "satisfaction_score",
            "is_partnered",
            "introduction",
            "city",
            "id_photo",
        ]


class InstructorCreateSerializer(
    serializers.ModelSerializer,
    PhoneCreateSerializerValidator,
    BasicSerializerValidator,
):
    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorUpdateSerializer(
    serializers.ModelSerializer,
    BasicSerializerValidator,
):
    def save(self, **kwargs):
        if not self.initial_data["phone"] == self.instance.phone:
            PhoneCreateSerializerValidator.validate_phone(self.initial_data["phone"])
        super().save(**kwargs)

    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = "__all__"


class InstructorCalendarSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class InstructorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        exclude = ["id", "hours_taught", "is_partnered"]


class InstructorReviewSerializer(serializers.ModelSerializer):
    pass


class InstructorFilterConditionSerializer(serializers.Serializer):
    module = ChoiceField(choices=AppModule.choices, default=AppModule.PLATFORM_MANAGEMENT)
