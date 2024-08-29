from typing import Dict, List

from django.db import transaction
from django.db.models import QuerySet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from apps.my_lectures.models import Advertisement, InstructorEnrolment
from apps.my_lectures.serializers.advertisement import (
    AdvertisementAdvertisementRegistrationSerializer,
)
from apps.platform_management.models import Instructor
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.response import Response


class AdvertisementViewSet(ModelViewSet):
    # permission_classes = [InstructorPermission]
    permission_classes = [AllowAny]
    queryset = Advertisement.objects.all()
    ACTION_MAP = {
        "advertisement_registration": AdvertisementAdvertisementRegistrationSerializer,
    }

    def list(self, request, *args, **kwargs):
        # 获取当前登录的讲师
        instructor: Instructor = self.request.user

        # 获取所有广告
        advertisements: QuerySet["Advertisement"] = Advertisement.objects.all()

        # 获取所有与当前讲师相关的申请
        instructor_enrolments: QuerySet["InstructorEnrolment"] = InstructorEnrolment.objects.filter(
            instructor=instructor)
        application_dict: Dict[int, str] = {app.advertisement.id: app.status for app in instructor_enrolments}

        # 准备返回的数据列表
        advertisement_list: List[dict] = []

        for ad in advertisements:
            # 使用预先查询的申请状态
            status = application_dict.get(ad.id, "pending")

            # 添加广告信息和状态到返回数据中
            advertisement_list.append({
                'id': ad.id,
                'training_class': ad.training_class.name,
                # 'number_of_registrations': ad.number_of_registrations,
                # 'registration_deadline': ad.registration_deadline,
                'status': status,
            })

        return Response(advertisement_list)

    @action(methods=["POST"], detail=False)
    def advertisement_registration(self, request, *args, **kwargs):
        validated_data = self.validated_data

        # 如果该广告不存在，直接返回
        try:
            advertisement: Advertisement = Advertisement.objects.get(id=validated_data["advertisement_id"])
        except Advertisement.DoesNotExist:
            return Response(result=False, err_msg="该广告不存在")

        with transaction.atomic():
            # 创建一条报名状况
            _, created = InstructorEnrolment.objects.get_or_create(
                instructor=self.request.user,
                advertisement_id=validated_data["advertisement_id"],
            )
            if not created:
                return Response(result=False, err_msg="已参加过报名")

            # 广告报名人数加1
            advertisement.enrolment_count += 1
            advertisement.save()

        return Response()
