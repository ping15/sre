# from django.contrib.auth import login
import random

from django.contrib.auth import logout
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from apps.authentication.serializers import LoginSerializer, SMSSerializer
from apps.platform_management.models import Administrator, Instructor, ClientStudent
from common.utils.auth import login, SMS_KEY
from common.utils.drf.response import Response


class AuthenticationViewSet(GenericViewSet):
    @action(methods=["POST"], detail=False, serializer_class=LoginSerializer)
    def login(self, request, *args, **kwargs):
        validated_data = self.validated_data
        phone, captcha_text = (
            validated_data["phone"],
            validated_data["captcha_text"],
        )
        user_models = [Administrator, Instructor, ClientStudent]
        user = None
        for user_model in user_models:
            try:
                user = user_model.objects.get(phone=phone)
                break
            except ObjectDoesNotExist:
                continue

        if not user:
            return Response(result=False, err_msg="不存在该手机号的用户")

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
        # sms_code = ''.join(random.choices('0123456789', k=6))
        sms_code = "666666"

        cache.set(f'{SMS_KEY}:{self.validated_data["phone"]}', sms_code, timeout=60)
        # send_sms(sms_code)

        return Response("发送成功")

    @property
    def validated_data(self):
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
