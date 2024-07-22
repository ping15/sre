import datetime
from datetime import timedelta
from typing import List, Dict

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.platform_management.models import Instructor
from apps.platform_management.serialiers.instructor import (
    InstructorListSerializer,
    InstructorCreateSerializer,
    InstructorCalendarSerializer,
    InstructorRetrieveSerializer,
    InstructorReviewSerializer,
)
from common.utils.calander import generate_calendar
from common.utils.excel_parser.mapping import INSTRUCTOR_EXCEL_MAPPING
from common.utils.modelviewset import ModelViewSet
from common.utils.permissions import InstructorPermission


class InstructorModelViewSet(ModelViewSet):
    permission_classes = [InstructorPermission]
    queryset = Instructor.objects.all()
    enable_batch_import = True
    batch_import_mapping = INSTRUCTOR_EXCEL_MAPPING
    batch_import_serializer = InstructorCreateSerializer

    ACTION_MAP = {
        "list": InstructorListSerializer,
        "create": InstructorCreateSerializer,
        "retrieve": InstructorRetrieveSerializer,
        "calendar": InstructorCalendarSerializer,
        "review": InstructorReviewSerializer,
    }

    # def get_serializer_class(self):
    #     return self.ACTION_MAP.get(self.action, InstructorListSerializer) # noqa

    # def list(self, request, *args, **kwargs):
    #     mock_data = [
    #         {
    #             "id": 1,
    #             "name": "张三",
    #             "email": "2345@qq.com",
    #             "phone": "13311111111",
    #             "password": "abcd123456",
    #             "hours_taught": 0,
    #             "satisfaction_score": 4.8,
    #             "is_partnered": True,
    #             "introduction": "深耕SRE 10年，有丰富的游戏运维经验",
    #         },
    #         {
    #             "id": 2,
    #             "name": "李四",
    #             "email": "2345@qq.com",
    #             "phone": "13311111111",
    #             "password": "abcd123456",
    #             "hours_taught": 0,
    #             "satisfaction_score": 4.8,
    #             "is_partnered": True,
    #             "introduction": "深耕SRE 10年，有丰富的游戏运维经验",
    #         },
    #         {
    #             "id": 3,
    #             "name": "王五",
    #             "email": "2345@qq.com",
    #             "phone": "13311111111",
    #             "password": "abcd123456",
    #             "hours_taught": 0,
    #             "satisfaction_score": 4.8,
    #             "is_partnered": True,
    #             "introduction": "深耕SRE 10年，有丰富的游戏运维经验",
    #         },
    #     ]
    #
    #     return Response({
    #         "count": 3,
    #         "next": None,
    #         "previous": None,
    #         "results": mock_data,
    #     })

    # def retrieve(self, request, *args, **kwargs):
    #     mock_data = {
    #         "name": "张三",
    #         "phone": "13311111111",
    #         "email": "2345@qq.com",
    #         "password": "abcd123456",
    #         "city": "深圳",
    #         "company": "腾讯科技有限公司",
    #         "department": "技术运营部",
    #         "position": "SRE工程师",
    #         "introduction": "深耕SRE 10年，有丰富的游戏运维经验",
    #         "teachable_courses": ["SRE 专家培训课(中级)", "SRE 专家培训课(高级)"],
    #         "satisfaction_score": 4.8,
    #     }
    #     return Response(mock_data)

    @action(methods=["GET"], detail=True)
    def taught_courses(self, request, *args, **kwargs):
        """已授课程"""
        # mock_data = [
        #     {
        #         "class_name": "SRE 专家培训课-1期",
        #         "start_date": "2023-04-12",
        #         "hours": 12,
        #         "target_client_company": "客户公司名称A",
        #     },
        #     {
        #         "class_name": "SRE 专家培训课-2期",
        #         "start_date": "2023-04-13",
        #         "hours": 12,
        #         "target_client_company": "客户公司名称B",
        #     },
        # ]

        taught_courses: List[Dict[str:str]] = []
        training_classes = self.get_object().training_classes.filter(
            start_date__lte=datetime.datetime.now()
        )

        for instance in training_classes:
            taught_courses.append(
                {
                    "name": instance.name,
                    "hours": instance.hours_per_lesson,
                    "start_date": instance.start_date,
                    "target_client_company": instance.target_client_company,
                }
            )

        return self.get_paginated_response(self.paginate_queryset(taught_courses))

    @action(methods=["GET"], detail=True)
    def calendar(self, request, *args, **kwargs):
        """日程"""
        # mock_data = {
        #     "code": 0,
        #     "msg": "",
        #     "results": [
        #         {
        #             "date": "2024-09-30",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-01",
        #             "is_available": True,
        #             "holiday": "国庆节",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-02",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-03",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [
        #                 {
        #                     "course_name": "SRE 专家培训课(中级)",
        #                     "target_client_company": "客户公司名称A",
        #                 },
        #                 {
        #                     "course_name": "SRE 专家培训课(高级)",
        #                     "target_client_company": "客户公司名称B",
        #                 },
        #             ],
        #             "count": 2
        #         },
        #         {
        #             "date": "2024-10-04",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-05",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-06",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-07",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [
        #                 {
        #                     "course_name": "SRE 专家培训课(中级)",
        #                     "target_client_company": "客户公司名称A",
        #                 },
        #             ],
        #             "count": 1
        #         },
        #         {
        #             "date": "2024-10-08",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-09",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-10",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-11",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-12",
        #             "is_available": False,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-13",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-14",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-15",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-16",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-17",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-18",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-19",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-20",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-21",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-22",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-23",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-24",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-25",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-26",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-27",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-28",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-29",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-30",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-10-31",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-01",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-02",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-03",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-04",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-05",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-06",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-07",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-08",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-09",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         },
        #         {
        #             "date": "2024-11-10",
        #             "is_available": True,
        #             "holiday": "",
        #             "data": [],
        #             "count": 0
        #         }
        #     ]
        # }
        # return Response(mock_data["results"])
        validated_data = self.validated_data

        # 培训班信息
        training_classes_info: List[dict] = [
            {
                "start_date": instance.start_date,
                "target_client_company": instance.target_client_company,
                "name": instance.name,
            }
            for instance in self.get_object().training_classes.all()
        ]
        date__daily_calendar_map: Dict[str, dict] = generate_calendar(
            validated_data["year"], validated_data["month"]
        )
        for programme in training_classes_info:
            start_date: datetime.date = programme.pop("start_date")
            formatted_start_date: str = start_date.strftime("%Y-%m-%d")
            formatted_next_date: str = (start_date + timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )

            # 更新当前日期的日历映射
            if formatted_start_date in date__daily_calendar_map:
                date__daily_calendar_map[formatted_start_date]["data"].append(programme)
                date__daily_calendar_map[formatted_start_date]["count"] += 1

            # 更新下一天的日历映射
            if formatted_next_date in date__daily_calendar_map:
                date__daily_calendar_map[formatted_next_date]["data"].append(programme)
                date__daily_calendar_map[formatted_next_date]["count"] += 1

        return Response(date__daily_calendar_map.values())

    @action(methods=["GET"], detail=True)
    def review(self, request, *args, **kwargs):
        """课后复盘"""
        mock_data = [
            {
                "course_name": "SRE 专家培训课(中级)",
                "target_client_company": "客户公司名称A",
                "finish_date": "2024-10-24",
                "review": "复盘内容......",
            },
            {
                "course_name": "SRE 专家培训课(高级)",
                "target_client_company": "客户公司名称B",
                "finish_date": "2024-10-25",
                "review": "复盘内容......",
            },
        ]
        return Response(mock_data)
