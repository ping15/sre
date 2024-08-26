from rest_framework.pagination import PageNumberPagination as DRFPagination
from rest_framework.response import Response


class PageNumberPagination(DRFPagination):
    page_query_param = "page"
    page_size_query_param = "pagesize"

    # def get_page_size(self, request):
    #     page_size = request.query_params.get("pagesize")
    #     if page_size == "-1":
    #         return None
    #     return super().get_page_size(request)

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "result": True,
                "data": data,
            }
        )
