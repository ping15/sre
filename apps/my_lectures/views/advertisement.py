import datetime
from datetime import timedelta
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
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.response import Response


class AdvertisementViewSet(ModelViewSet):
    # permission_classes = [InstructorPermission]
    permission_classes = [AllowAny]
    queryset = Advertisement.objects.all()
    ACTION_MAP = {
        "advertisement_registration": AdvertisementAdvertisementRegistrationSerializer,
    }

    def get_queryset(self):
        # 所有讲师报名表处于[待聘用]状态且过了deadline的状态都更新为[已超时]
        InstructorEnrolment.objects.filter(
            status=InstructorEnrolment.Status.PENDING,
            advertisement__deadline_datetime__lte=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
        ).update(status=InstructorEnrolment.Status.TIMEOUT)
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        # 获取当前登录的讲师
        instructor: Instructor = self.request.user

        # 获取所有广告
        advertisements: QuerySet["Advertisement"] = Advertisement.objects.all()

        # 获取所有与当前讲师相关的申请
        instructor_enrolments: QuerySet["InstructorEnrolment"] = InstructorEnrolment.objects.filter(
            instructor=instructor)
        application_dict: Dict[int, str] = {app.advertisement.id: app.status for app in instructor_enrolments}

        advertisement_list: List[dict] = []
        now: datetime.datetime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)

        for ad in advertisements:
            # 使用预先查询的申请状态
            status = application_dict.get(
                ad.id, InstructorEnrolment.Status.NOT_ENROLLED
                if ad.deadline_datetime > now else InstructorEnrolment.Status.TIMEOUT
            )

            training_class: TrainingClass = ad.training_class

            # 添加广告信息和状态到返回数据中
            advertisement_list.append({
                "id": ad.id,
                "position": ad.location,
                "training_class": {
                    "course": {
                        "name": training_class.course.name,
                        "level": training_class.course.level,
                    },
                    "start_date": training_class.start_date,
                    "end_date": training_class.start_date + timedelta(days=1),
                    "target_client_company_name": training_class.target_client_company_name,
                },
                "deadline": ad.deadline_datetime,
                "status": status,
                "enrolment_count": ad.enrolment_count,
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

        # 如果该广告已过期，不可报名
        if advertisement.deadline_datetime <= datetime.datetime.now().replace(tzinfo=datetime.timezone.utc):
            return Response(result=False, err_msg="该广告已过期")

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
