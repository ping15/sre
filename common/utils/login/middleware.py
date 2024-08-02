from blueapps.account.handlers.response import ResponseHandler
from blueapps.account.conf import ConfFixture
from django.contrib import auth
from django.core.cache import caches
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from common.utils.login.forms import AuthenticationForm

cache = caches["login_db"]


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        Login paas by two ways
        1. views decorated with 'login_exempt' keyword
        2. User has logged in calling authentication.login
        """
        if hasattr(request, "is_wechat") and request.is_wechat():
            return None

        if hasattr(request, "is_bk_jwt") and request.is_bk_jwt():
            return None

        if hasattr(request, "is_rio") and request.is_rio():
            return None

        if getattr(view, "login_exempt", False):
            return None

        user = self.authenticate(request)
        if user:
            return None

        handler = ResponseHandler(ConfFixture, settings)
        return handler.build_401_response(request)

    def process_response(self, request, response):
        return response

    def authenticate(self, request):
        form = AuthenticationForm(request.COOKIES)
        if not form.is_valid():
            return None

        bk_token = form.cleaned_data["bk_token"]
        session_key = request.session.session_key
        if session_key:
            # 确认 cookie 中的 ticket 和 cache 中的是否一致
            cache_session = cache.get(session_key)
            is_match = cache_session and bk_token == cache_session.get("bk_token")
            if is_match and request.user.is_authenticated:
                return request.user

        user = auth.authenticate(request=request, bk_token=bk_token)
        if user is not None and user.username != request.user.username:
            auth.login(request, user)

        if user is not None and request.user.is_authenticated:
            # 登录成功，重新调用自身函数，即可退出
            cache.set(session_key, {"bk_token": bk_token}, settings.LOGIN_CACHE_EXPIRED)
            return self.authenticate(request)
        return user
