import os
from typing import Any, Dict, List

from django.http import FileResponse, Http404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet as DRFModelViewSet

from common.utils.cos import cos_client
from common.utils.drf.filters import BaseFilterSet
from common.utils.drf.pagination import PageNumberPagination
from common.utils.drf.response import Response
from common.utils.excel_parser.parser import excel_to_list


class BatchImportSerializer(serializers.Serializer):
    file_key = serializers.CharField()


class SimpleQuerySerializer(serializers.Serializer):
    query = serializers.CharField()


class ModelViewSet(DRFModelViewSet):
    # 批量导入设置
    enable_batch_import = False
    batch_import_serializer = None
    batch_import_template_path = ""
    batch_import_mapping = {}

    # 视图 -> 序列化器
    ACTION_MAP = {}

    # 视图 -> 权限
    PERMISSION_MAP = {}

    # 筛选类
    filter_class = BaseFilterSet

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.enable_batch_import and hasattr(cls, "batch_import"):
            cls.batch_import = cls.batch_import_template = None
        else:
            cls.ACTION_MAP["batch_import"] = BatchImportSerializer
            cls.batch_import_serializer = cls.batch_import_serializer or cls.ACTION_MAP.get("create")

        cls.ACTION_MAP["simple_query"] = SimpleQuerySerializer

    def get_permissions(self):
        self.permission_classes = self.PERMISSION_MAP.get(self.action, self.permission_classes)  # noqa
        return super().get_permissions()

    def get_serializer_class(self):
        return self.ACTION_MAP.get(self.action, self.serializer_class)  # noqa

    @property
    def validated_data(self):
        data = self.request.query_params if self.request.method == "GET" else self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def paginate_data(self, datas: List[Any]) -> List[Any]:
        return self.get_paginated_response(self.paginate_queryset(datas)).data["data"]

    @staticmethod
    def transform_choices(choices):
        return [{"id": value, "name": label} for value, label in choices]

    def list(self, request, *args, **kwargs):
        if PageNumberPagination.page_size_query_param not in self.request.query_params:
            return Response(self.get_serializer(self.filter_queryset(self.get_queryset()), many=True).data)

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return Response(super().retrieve(request, *args, **kwargs).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True if isinstance(request.data, list) else False)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, instance=serializer.instance)

    def update(self, request, *args, **kwargs):
        return Response(super().update(request, *args, **kwargs).data)

    def destroy(self, request, *args, **kwargs):
        return Response(super().destroy(request, *args, **kwargs).data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def filter_condition(self, request, *args, **kwargs):
        return NotImplemented("条件筛选")

    @action(methods=["POST"], detail=False)
    def batch_import(self, request, *args, **kwargs):
        """批量导入"""
        validated_data = self.validated_data

        # 从cos中下载文件
        response: dict = cos_client.download_file(validated_data["file_key"])
        if response.get("error"):
            return Response(result=False, err_msg=response["error"])

        # 解析excel
        datas: List[Dict[str, str]] = excel_to_list(response["Body"].read(None), self.batch_import_mapping)

        create_serializer = self.batch_import_serializer(data=datas, many=True)

        if not create_serializer.is_valid():
            return Response(data=[], result=False, err_msg=str(create_serializer.errors))

        return Response(create_serializer.validated_data)

    @action(methods=["GET"], detail=False)
    def batch_import_template(self, request, *args, **kwargs):
        if not os.path.exists(self.batch_import_template_path):
            raise Http404("Template file does not exist")

        return FileResponse(
            open(self.batch_import_template_path, "rb"),
            as_attachment=True,
            filename=os.path.basename(self.batch_import_template_path),
        )

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def simple_query(self, request, *args, **kwargs):
        validated_data = self.validated_data
        return Response(list(self.queryset.values(*validated_data["query"].split(","))))
