import datetime
from typing import Any, Dict

from django.db import transaction
from django.db.models import F, QuerySet
from rest_framework.decorators import action

from apps.my_lectures.filters.advertisement import AdvertisementFilterClass
from apps.my_lectures.handles.event import EventHandler
from apps.my_lectures.models import Advertisement, InstructorEnrolment
from apps.my_lectures.serializers.advertisement import (
    AdvertisementAdvertisementCancelSerializer,
    AdvertisementAdvertisementRegistrationSerializer,
)
from apps.platform_management.models import CourseTemplate, Instructor
from apps.teaching_space.models import TrainingClass
from common.utils.drf.modelviewset import ModelViewSet
from common.utils.drf.permissions import InstructorPermission
from common.utils.drf.response import Response


class AdvertisementViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    queryset = Advertisement.objects.all()
    filter_class = AdvertisementFilterClass
    ACTION_MAP = {
        "advertisement_registration": AdvertisementAdvertisementRegistrationSerializer,
        "advertisement_cancel": AdvertisementAdvertisementCancelSerializer,
    }

    def get_queryset(self):
        now: datetime.datetime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)

        # 所有讲师报名表处于[待聘用]状态且过了deadline的状态都更新为[已超时]
        InstructorEnrolment.objects. \
            filter(status=InstructorEnrolment.Status.PENDING, advertisement__deadline_datetime__lte=now). \
            update(status=InstructorEnrolment.Status.TIMEOUT)
        return super().get_queryset().filter(deadline_datetime__gt=now)

    def list(self, request, *args, **kwargs):
        # 获取当前登录的讲师
        instructor: Instructor = self.request.user

        # 获取所有广告
        advertisements: QuerySet["Advertisement"] = self.filter_queryset(self.get_queryset())

        # 获取所有与当前讲师相关的申请
        instructor_enrolments: QuerySet["InstructorEnrolment"] = InstructorEnrolment.objects. \
            filter(instructor=instructor)
        enrolment_status_map: Dict[int, str] = {ie.advertisement.id: ie.status for ie in instructor_enrolments}

        advertisement_info: Dict[str, Any] = {
            "overview": {
                InstructorEnrolment.Status.ACCEPTED: 0,  # 已被聘用, 已撤销
                InstructorEnrolment.Status.PENDING: 0,  # 等待确认
                InstructorEnrolment.Status.REJECTED: 0,  # 未被聘用
            },
            "datas": [],
        }
        for ad in advertisements:
            # 使用预先查询的申请状态
            status = enrolment_status_map.get(ad.id, InstructorEnrolment.Status.NOT_ENROLLED)

            training_class: TrainingClass = ad.training_class

            # 分类统计
            if status in advertisement_info["overview"].keys():
                advertisement_info["overview"][status] += 1

            # 已撤销也归类到[已被聘用]中
            elif status == InstructorEnrolment.Status.REVOKE:
                advertisement_info["overview"][InstructorEnrolment.Status.ACCEPTED] += 1

            # 添加广告信息和状态到返回数据中
            advertisement_info["datas"].append({
                "id": ad.id,
                # 上课地点
                "location": ad.location,
                "training_class": {
                    "course": {
                        # 课程名
                        "name": training_class.course.name,
                        # 课程级别
                        "level": training_class.course.level,
                    },
                    # 培训班开课时间
                    "start_date": training_class.start_date,
                    # 培训班结课时间
                    "end_date": training_class.end_date,
                    # 目标客户公司
                    "target_client_company_name": training_class.target_client_company_name,
                },
                # 截至时间
                "deadline_datetime": ad.deadline_datetime.strftime("%Y-%m-%d %H:%M"),
                # 广告状态
                "status": InstructorEnrolment.Status.REVOKE if ad.is_revoked else status,
                # 报名人数
                "enrolment_count": ad.enrolment_count,
            })

        return Response(advertisement_info)

    @action(methods=["POST"], detail=False)
    def advertisement_registration(self, request, *args, **kwargs):
        """广告报名"""
        validated_data = self.validated_data

        # 如果该广告不存在，直接返回
        try:
            advertisement: Advertisement = Advertisement.objects.get(id=validated_data["advertisement_id"])
        except Advertisement.DoesNotExist:
            return Response(result=False, err_msg="该广告不存在")

        # 如果该广告已过期，不可报名
        if advertisement.deadline_datetime <= datetime.datetime.now().replace(tzinfo=datetime.timezone.utc):
            return Response(result=False, err_msg="该广告已过期")

        # 是否该讲师有空给该培训班上课
        if not EventHandler.is_instructor_idle(
            instructor=self.request.user,
            start_date=advertisement.training_class.start_date,
            end_date=advertisement.training_class.end_date
        ):
            return Response(result=False, err_msg="该广告与原有日程有冲突，不可报名")

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

    @action(methods=["POST"], detail=False)
    def advertisement_cancel(self, request, *args, **kwargs):
        """取消报名"""
        validated_data = self.validated_data

        with transaction.atomic():
            # 删除报名记录
            deleted, _ = InstructorEnrolment.objects.filter(
                instructor=self.request.user,
                advertisement_id=validated_data["advertisement_id"],
                status=InstructorEnrolment.Status.PENDING,
            ).delete()

            if not deleted:
                return Response(result=False, err_msg="找不到该报名记录")

            # 广告报名人数减1
            Advertisement.objects.filter(id=validated_data["advertisement_id"]).update(
                enrolment_count=F('enrolment_count') - 1)

        return Response()

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        """筛选条件"""
        return Response([
            {"id": "course_name", "name": "课程名称", "children": []},
            {"id": "position", "name": "上课地点", "children": []},
            {"id": "course_level", "name": "课程等级", "children": [
                {"id": level.value, "name": level.label} # noqa
                for level in CourseTemplate.Level
            ]},
        ])
