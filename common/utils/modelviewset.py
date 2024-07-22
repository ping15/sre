from typing import List, Dict

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet as DRFModelViewSet

from common.utils.excel_parser.parser import excel_to_list


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()


class ModelViewSet(DRFModelViewSet):
    enable_batch_import = False
    batch_import_serializer = None
    batch_import_mapping = {}
    ACTION_MAP = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.enable_batch_import and hasattr(cls, "batch_import"):
            cls.batch_import = None
        else:
            cls.ACTION_MAP["batch_import"] = FileSerializer

    def get_serializer_class(self):
        return self.ACTION_MAP.get(self.action, self.serializer_class)  # noqa

    @property
    def validated_data(self):
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @action(methods=["POST"], detail=False)
    def batch_import(self, request, *args, **kwargs):
        """批量导入"""
        validated_data = self.validated_data
        datas: List[Dict[str, str]] = excel_to_list(
            validated_data["file"], self.batch_import_mapping
        )
        create_serializer = self.batch_import_serializer(data=datas, many=True)
        if create_serializer.is_valid():
            create_serializer.save()

        err_msg = create_serializer.errors
        return Response(
            {
                "results": True if not err_msg else False,
                "err_msg": str(err_msg),
            }
        )
