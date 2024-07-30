from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError

from common.utils.drf.response import Response


def exception_handler(exc, context):
    # 调用 DRF 默认的异常处理器以获得标准的错误响应。
    response = drf_exception_handler(exc, context)

    # 如果异常是 ValidationError，重写响应格式
    if isinstance(exc, ValidationError):
        return Response(status=exc.status_code, err_msg=exc.detail, result=False)

    # 处理其他类型的异常，如果有的话，可以在这里添加自定义处理
    if response is not None:
        response.data["status_code"] = response.status_code

    return response
