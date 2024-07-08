from rest_framework.pagination import PageNumberPagination as DRFPagination


class PageNumberPagination(DRFPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"
