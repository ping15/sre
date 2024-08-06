from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotAuthenticated,
)

from common.utils.drf.response import Response


def exception_handler(exc, context):
    # 调用 DRF 默认的异常处理器以获得标准的错误响应。
    response = drf_exception_handler(exc, context)

    custom_exceptions = (
        ValidationError,
        PermissionDenied,
        NotAuthenticated,
    )
    if isinstance(exc, custom_exceptions):
        exc_detail = exc.detail
        if isinstance(exc_detail, list):
            exc_detail = ([detail for detail in exc.detail if detail],)
        return Response(status=exc.status_code, err_msg=exc_detail, result=False)

    # 处理其他类型的异常，如果有的话，可以在这里添加自定义处理
    if response is not None:
        response.data["status_code"] = response.status_code

    return response
