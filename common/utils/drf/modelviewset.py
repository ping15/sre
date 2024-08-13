from typing import List, Dict

from django.http import Http404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet as DRFModelViewSet

from common.utils.drf.filters import BaseFilterSet
from common.utils.drf.response import Response
from common.utils.excel_parser.parser import excel_to_list


class FileSerializer(serializers.Serializer):
    file_path = serializers.CharField()


class SimpleQuerySerializer(serializers.Serializer):
    query = serializers.CharField()


class ModelViewSet(DRFModelViewSet):
    # 是否支持批量导入
    enable_batch_import = False
    batch_import_serializer = None
    batch_import_mapping = {}

    # 默认序列化器
    default_serializer_class = None

    # 备份filter_backend
    origin_filter_backend = api_settings.DEFAULT_FILTER_BACKENDS

    # 视图 -> 序列化器
    ACTION_MAP = {}

    # 筛选, fuzzy: 模糊匹配, time/datetime: 时间匹配, property: 属性匹配,
    filter_class = BaseFilterSet
    copy_filter_class = filter_class
    # string模糊匹配
    string_fuzzy_filter_fields = []
    # integer匹配
    integer_filter_fields = []
    # time匹配
    time_filter_fields = []
    # datetime匹配
    datetime_filter_fields = []
    # property模糊匹配
    property_fuzzy_filter_fields = []

    # 页面关键词 -> 字段
    filter_condition_mapping = {}
    filter_condition_enum_list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.enable_batch_import and hasattr(cls, "batch_import"):
            cls.batch_import = None
        else:
            cls.ACTION_MAP["batch_import"] = FileSerializer
            if not cls.batch_import_serializer:
                cls.batch_import_serializer = cls.ACTION_MAP.get("create")

        cls.ACTION_MAP["simple_query"] = SimpleQuerySerializer

    def disable_filter_backend(self):
        self.origin_filter_backend = self.filter_backends
        self.filter_backends = []

    def enable_filter_backend(self):
        self.filter_backends = self.origin_filter_backend

    def get_queryset(self):
        queryset = super().get_queryset()

        # filter_class = self.filter_class
        # if issubclass(filter_class, BaseFilterSet):
        #     filter_class.setup_filters(
        #         model=self.queryset.model,
        #         string_fuzzy_filter_fields=self.string_fuzzy_filter_fields,
        #         time_filter_fields=self.time_filter_fields,
        #         property_fuzzy_filter_fields=self.property_fuzzy_filter_fields,
        #         datetime_filter_fields=self.datetime_filter_fields,
        #         integer_filter_fields=self.integer_filter_fields,
        #     )

        return queryset

    def get_serializer_class(self):
        return self.ACTION_MAP.get(self.action, self.default_serializer_class)  # noqa

    @property
    def validated_data(self):
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=True if isinstance(request.data, list) else False
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return Response(super().update(request, *args, **kwargs).data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response(result=False, err_msg=e.args[0])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        response_data = []

        for display_name, field_name in self.filter_condition_mapping.items():
            item = {"id": field_name, "name": display_name, "children": []}

            response_data.append(item)

        return Response(response_data)

    @action(methods=["POST"], detail=False)
    def batch_import(self, request, *args, **kwargs):
        """批量导入"""
        validated_data = self.validated_data
        datas: List[Dict[str, str]] = excel_to_list(
            validated_data["file_path"], self.batch_import_mapping
        )
        create_serializer = self.batch_import_serializer(data=datas, many=True)

        if not create_serializer.is_valid():
            return Response(
                data=[], result=False, err_msg=str(create_serializer.errors)
            )

        return Response(create_serializer.validated_data)

    @action(methods=["GET"], detail=False)
    def simple_query(self, request, *args, **kwargs):
        validated_data = self.validated_data
        return Response(list(self.queryset.values(*validated_data["query"].split(","))))
