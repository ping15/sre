from rest_framework.pagination import PageNumberPagination as DRFPagination


class PageNumberPagination(DRFPagination):
    page_query_param = "page"
    page_size_query_param = "pagesize"

    # def paginate_queryset(self, queryset, request, view=None):
    #     a = super().paginate_queryset(queryset, request, view)
    #     return a
