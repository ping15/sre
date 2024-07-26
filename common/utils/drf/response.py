from rest_framework.response import Response as DRFResponse


class Response(DRFResponse):
    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        result=True,
        err_msg="",
    ):
        response_data = {"result": result, "err_msg": err_msg, "data": data}
        super().__init__(
            data=response_data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )
