import os
import random
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from django.db import transaction
from django.db.models import QuerySet
from django.http import FileResponse, Http404, QueryDict
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet as DRFModelViewSet

from apps.my_learning.serializers.historical_grades import (
    HistoricalGradesListSerializer,
)
from apps.platform_management.models import ClientStudent
from apps.teaching_space.models import TrainingClass
from common.utils.cos import cos_client
from common.utils.drf.filters import BaseFilterSet
from common.utils.drf.pagination import PageNumberPagination
from common.utils.drf.response import Response
from common.utils.excel_parser.parser import excel_to_list
from common.utils.tools import query_debugger
from exam_system.models import ExamStudent


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

    def get_permissions(self):
        self.permission_classes = self.PERMISSION_MAP.get(self.action, self.permission_classes)  # noqa
        return super().get_permissions()

    def get_serializer_class(self):
        return self.ACTION_MAP.get(self.action, self.serializer_class)  # noqa

    # region 增删改查
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

    @query_debugger
    def create_for_user(self, model, request, update_serializer=None, create_serializer=None, *args, **kwargs):
        update_serializer = update_serializer or self.ACTION_MAP["update"]
        create_serializer = create_serializer or self.ACTION_MAP["create"]

        initial_data = request.data
        if not isinstance(initial_data, list):
            return self.create(request, *args, **kwargs)

        objs_to_create, objs_to_update = [], []
        try:
            phones: List[str] = [obj["phone"] for obj in initial_data]
        except KeyError:
            return Response(result=False, err_msg="未传入手机号")

        # 已存在的模型实例列表
        existing_objs: QuerySet[model] = model.objects.filter(phone__in=phones)
        # 手机号 -> 已存在的模型实例
        phone_to_obj: Dict[str, model] = {obj.phone: obj for obj in existing_objs}
        # 需要更新的字段
        update_fields = [field.name for field in model._meta.fields if field.name != "id"]
        for obj_info in initial_data:
            phone = obj_info["phone"]

            if phone in phone_to_obj:
                # 字段更新
                obj: model = phone_to_obj[phone]
                serializer = update_serializer(instance=obj, data=obj_info)
                serializer.is_valid(raise_exception=True)
                for attr, value in serializer.validated_data.items():
                    setattr(obj, attr, value)
                objs_to_update.append(obj)
            else:
                # 创建实例
                serializer = create_serializer(data=obj_info)
                serializer.is_valid(raise_exception=True)
                objs_to_create.append(model(**serializer.validated_data))

        with transaction.atomic():
            model.objects.bulk_update(objs_to_update, update_fields, batch_size=500)
            model.objects.bulk_create(objs_to_create, batch_size=500)

        objs_to_create = list(model.objects.filter(phone__in=[obj.phone for obj in objs_to_create]))

        return Response(status=status.HTTP_201_CREATED, instance=objs_to_create + objs_to_update)

    def update(self, request, *args, **kwargs):
        return Response(super().update(request, *args, **kwargs).data)

    def destroy(self, request, *args, **kwargs):
        return Response(super().destroy(request, *args, **kwargs).data, status=status.HTTP_200_OK)
    # endregion

    # region 批量导入
    @action(methods=["POST"], detail=False)
    def batch_import(self, request, *args, **kwargs):
        """批量导入"""
        validated_data = self.validated_data

        # 从cos中下载文件
        response: dict = cos_client.download_file(validated_data["file_key"])
        if response.get("error"):
            return Response(result=False, err_msg=response["error"])

        # 解析excel
        datas, err_msg = excel_to_list(response["Body"].read(None), self.batch_import_mapping)
        if err_msg:
            return Response(result=False, err_msg=err_msg)

        create_serializer = self.batch_import_serializer(data=datas, many=True)

        create_serializer.is_valid(raise_exception=True)

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
    # endregion

    # region 私有函数
    @property
    def validated_data(self):
        data = self.request.query_params if self.request.method == "GET" else self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def paginate_response(self, datas: List[Any]) -> Response:
        return self.get_paginated_response(self.paginate_queryset(datas))

    @staticmethod
    def transform_choices(choices):
        return [{"id": value, "name": label} for value, label in choices]

    def build_student_grades_response(self, student: ClientStudent, query_params: QueryDict):
        # 当前考生所有已考过的历史成绩
        exam_students = ExamStudent.objects.filter(student_name=student.username, password=student.phone, is_commit=1)

        # 培训班id相同的聚合在一起
        training_class_id_to_grades, training_class_ids = defaultdict(list), set()
        for grade in HistoricalGradesListSerializer(exam_students, many=True).data:
            training_class_id_to_grades[grade["exam_info"]["training_class_id"]].append(grade)
            training_class_ids.add(grade["exam_info"].pop("training_class_id"))

        training_class_id_to_name = {tc.id: tc.name for tc in TrainingClass.objects.filter(id__in=training_class_ids)}

        # 添加额外数据并组装
        grade_infos: List[dict] = [
            {
                "training_class_name": training_class_id_to_name.get(training_class_id, ""),
                "grades": grades,
                "score": sum(grade["exam_info"]["score"] for grade in grades) if len(grades) >= 2 else None,
                "is_pass": random.choice([True, False]) if len(grades) >= 2 else None,
            }
            for training_class_id, grades in training_class_id_to_grades.items()
        ]

        # 筛选
        grade_infos = self._filter_grades(grade_infos, query_params)
        return self.get_paginated_response(self.paginate_queryset(grade_infos))

    @staticmethod
    def _filter_grades(grade_infos: List[dict], query_params: QueryDict) -> List[dict]:
        """筛选学员成绩"""

        training_class_name = query_params.get("training_class_name")
        exam_title = query_params.get("exam_title")
        start_datetime_before = query_params.get("start_datetime_before")
        start_datetime_after = query_params.get("start_datetime_after")

        if not any([training_class_name, exam_title, start_datetime_before, start_datetime_after]):
            return grade_infos

        filtered_grades = []
        for grade_info in grade_infos:
            # 筛选培训班名称
            if training_class_name and training_class_name in grade_info["training_class_name"]:
                filtered_grades.append(grade_info)
                continue

            # 只要有一个符合则整个展示
            for grade_detail in grade_info["grades"]:
                # 筛选考试名称
                if exam_title and exam_title in grade_detail["exam_info"]["title"]:
                    filtered_grades.append(grade_info)
                    break

                # 筛选开考时间
                start_time: str = grade_detail["start_time"]
                if start_time and start_datetime_after and start_datetime_before:
                    if datetime.fromisoformat(start_datetime_after) <= datetime.fromisoformat(start_time) \
                            <= datetime.fromisoformat(start_datetime_before):
                        filtered_grades.append(grade_info)
                        break

        return filtered_grades

    # endregion
