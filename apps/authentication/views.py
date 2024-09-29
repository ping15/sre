import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.authentication.serializers import LoginSerializer, SMSSerializer
from apps.platform_management.models import Administrator, ClientStudent, Instructor
from common.utils.auth import SMS_KEY, SMS_SEND_TIMESTAMP_KEY, login
from common.utils.drf.response import Response
from common.utils.sms import send_sms


class AuthenticationViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @action(methods=["POST"], detail=False, serializer_class=LoginSerializer)
    def login(self, request, *args, **kwargs):
        validated_data = self.validated_data
        phone, captcha_text = (
            validated_data["phone"],
            validated_data["captcha_text"],
        )
        user = self.get_user_by_phone(phone)

        if not user:
            return Response(result=False, err_msg="不存在该手机号的用户")

        if settings.ENABLE_SMS:
            cached_captcha_text = cache.get(f'{SMS_KEY}:{self.validated_data["phone"]}')
            if not cached_captcha_text:
                return Response(result=False, err_msg="未发送验证码或验证码已失效")

            if captcha_text != cached_captcha_text:
                return Response(result=False, err_msg="验证码错误")

        login(request, user)
        return Response({"role": user.role, "username": user.username})

    @action(methods=["GET"], detail=False)
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response()

    @action(methods=["POST"], detail=False, serializer_class=SMSSerializer)
    def send_sms(self, request, *args, **kwargs):
        phone = self.validated_data["phone"]
        user = self.get_user_by_phone(phone)
        if not user:
            return Response(result=False, err_msg="不存在该手机号的用户")

        # 获取上次发送的时间戳，存在则对比时间间隔
        last_send_time = cache.get(f"{SMS_SEND_TIMESTAMP_KEY}:{phone}")
        if last_send_time and timezone.now() - last_send_time < timedelta(seconds=60):
            return Response(
                result=False,
                err_msg="请等待60秒后再发送验证码",
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        sms_code = ''.join(random.choices('0123456789', k=6)) if settings.ENABLE_SMS else "666666"

        # 设置验证码和发送时间戳到缓存
        cache.set(f"{SMS_KEY}:{phone}", sms_code, timeout=60)
        cache.set(f"{SMS_SEND_TIMESTAMP_KEY}:{phone}", timezone.now(), timeout=60)

        if settings.ENABLE_SMS:
            send_sms(phone, sms_code)

        return Response("发送成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    # @action(methods=["GET"], detail=False)
    def permissions(self, request, *args, **kwargs):
        return Response(
            {
                "role": request.user.role,
                "username": request.user.username,
                "manage_company_id": request.user.affiliated_manage_company_id
                if isinstance(request.user, Administrator) else None,
            }
        )

    @property
    def validated_data(self):
        data = self.request.query_params if self.request.method == "GET" else self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @staticmethod
    def get_user_by_phone(phone):
        """
        根据手机号在给定的用户模型列表中查找用户。

        :param phone: 用户的手机号
        :return: 找到的用户对象或 None
        """
        user_models = [Administrator, Instructor, ClientStudent]
        for user_model in user_models:
            try:
                user = user_model.objects.get(phone=phone)
                return user
            except ObjectDoesNotExist:
                continue
        return None
