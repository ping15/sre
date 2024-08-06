from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from apps.authentication.serializers import LoginSerializer
from apps.platform_management.models import Administrator, Instructor, ClientStudent
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
                if captcha_text == "666666":
                    user = user_model.objects.get(phone=phone)
                    break
            except ObjectDoesNotExist:
                continue

        if user:
            login(
                request,
                user,
                backend="apps.authentication.backends.MultiUserModelBackend",
            )

            return Response()

        return Response(result=False, err_msg="登录失败")

    @property
    def validated_data(self):
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
