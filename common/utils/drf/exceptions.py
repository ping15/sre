from rest_framework.exceptions import (NotAuthenticated, ParseError,
                                       PermissionDenied, ValidationError)
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import exception_handler as drf_exception_handler

from common.utils.drf.response import Response


def exception_handler(exc, context):
    # 调用 DRF 默认的异常处理器以获得标准的错误响应。
    response = drf_exception_handler(exc, context)

    custom_exceptions = (
        ValidationError,
        PermissionDenied,
        NotAuthenticated,
        ParseError,
    )
    if isinstance(exc, custom_exceptions):
        exc_detail = exc.detail
        status_code = (
            HTTP_401_UNAUTHORIZED
            if isinstance(exc, NotAuthenticated)
            else exc.status_code
        )
        return Response(status=status_code, err_msg=str(exc_detail), result=False)

    # 处理其他类型的异常，如果有的话，可以在这里添加自定义处理
    if response is not None:
        response.data["status_code"] = response.status_code

    return response
