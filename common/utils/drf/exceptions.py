from itertools import chain
from typing import Dict, List, Union

from rest_framework import serializers
from rest_framework.exceptions import (
    ErrorDetail,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import exception_handler as drf_exception_handler

from common.utils.drf.response import Response


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    custom_exceptions = (ValidationError, PermissionDenied, NotAuthenticated, ParseError)
    if isinstance(exc, custom_exceptions):
        exc_detail = exc.detail
        status_code = HTTP_401_UNAUTHORIZED if isinstance(exc, NotAuthenticated) else exc.status_code

        return Response(status=status_code, err_msg=handler_error_details(exc_detail), result=False)

    return response


def handler_error_details(
    details: Union[
        Dict[str, Union[List[ErrorDetail], ErrorDetail]],
        List[Union[
            ErrorDetail,
            Dict[str, List[ErrorDetail]]
        ]],
        ErrorDetail,
    ]
) -> str:
    if isinstance(details, dict):
        details = list(chain.from_iterable(
            [v for v in value] if isinstance(value, list) else [value]
            for _, value in details.items()
        ))

    elif isinstance(details, ErrorDetail):
        details = [details]

    elif isinstance(details, list) and all(isinstance(item, dict) for item in details):
        details = [value for item in details if item for value in list(item.values())[0] if value]

    err_msg = "\n".join(f"{str(value)}" for i, value in enumerate(details))

    err_msg = err_msg[:100] + "..." if len(err_msg) > 100 else err_msg

    return err_msg


class TrainingClassScheduleConflictError(serializers.ValidationError):
    status_code = 10000
    default_detail = '培训班出现排期冲突'

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
