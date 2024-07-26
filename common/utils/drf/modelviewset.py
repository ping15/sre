from typing import List, Dict

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet as DRFModelViewSet

from common.utils.drf.filters import MyModelFilterSet
from common.utils.drf.response import Response
from common.utils.excel_parser.parser import excel_to_list


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()


class SimpleQuerySerializer(serializers.Serializer):
    query = serializers.CharField()


class ModelViewSet(DRFModelViewSet):
    enable_batch_import = False
    batch_import_serializer = None
    batch_import_mapping = {}
    default_serializer_class = None
    ACTION_MAP = {}
    fuzzy_filter_fields = []
    time_filter_fields = []
    # todo
    filter_class = MyModelFilterSet
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

    def get_queryset(self):
        queryset = super().get_queryset()

        if hasattr(self, "fuzzy_filter_fields") or hasattr(self, "time_filter_fields"):
            filter_class = self.filter_class
            filter_class.setup_custom_filters(
                model=self.queryset.model,
                fuzzy_filter_fields=self.fuzzy_filter_fields,
                time_filter_fields=self.time_filter_fields,
            )

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

    @action(methods=["GET"], detail=False)
    def filter_condition(self, request, *args, **kwargs):
        response_data = []

        # 获取模型的 queryset
        queryset = self.get_queryset()

        for display_name, field_name in self.filter_condition_mapping.items():
            item = {"id": field_name, "name": display_name, "enum": []}

            if field_name in self.filter_condition_enum_list:
                # 获取字段的所有唯一值作为枚举结果
                unique_values = queryset.values_list(field_name, flat=True).distinct()
                item["enum"] = list(unique_values)

            response_data.append(item)

        return Response(response_data)

    @action(methods=["POST"], detail=False)
    def batch_import(self, request, *args, **kwargs):
        """批量导入"""
        validated_data = self.validated_data
        datas: List[Dict[str, str]] = excel_to_list(
            validated_data["file"], self.batch_import_mapping
        )
        create_serializer = self.batch_import_serializer(data=datas, many=True)

        err_msg: str = ""
        if not create_serializer.is_valid():
            err_msg = str(create_serializer.errors)

        return Response(
            create_serializer.validated_data,
            result=True if not err_msg else False,
            err_msg=err_msg,
        )

    @action(methods=["GET"], detail=False)
    def simple_query(self, request, *args, **kwargs):
        validated_data = self.validated_data
        return Response(list(self.queryset.values(*validated_data["query"].split(","))))
