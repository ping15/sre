import json
import traceback

from django.http import JsonResponse


class Capture500Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            return self.process_exception(request, e)
        return response

    def process_exception(self, request, exception):
        error_details = {
            'path': request.path,
            'method': request.method,
            'exception': str(exception),
            'traceback': traceback.format_exc().splitlines()
        }

        with open('error_log.json', 'w') as f:
            json.dump(error_details, f, indent=4)

        return JsonResponse({'result': False, 'err_msg': "服务器异常，详情查看日志", 'code': 400}, status=500)
