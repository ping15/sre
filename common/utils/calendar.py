import datetime
import json
from typing import Dict, List, Generator

from django.db.models import QuerySet

from apps.teaching_space.models import TrainingClass


# def parse_holiday_file(holiday_filepath: str) -> dict:
#     with open(holiday_filepath, "r", encoding="utf-8") as f:
#         days: list = json.load(f).get("days", [])
#
#     seen: set = set()
#     unique_days: list = []
#     for day in days:
#         if day["name"] not in seen:
#             unique_days.append(day)
#             seen.add(day["name"])
#
#     return {day["date"]: day["name"] for day in unique_days}
#
#
# def get_date_info(date: datetime.date, date__holiday_map: dict):
#     return {
#         "date": date.strftime("%Y-%m-%d"),
#         "is_available": True,
#         "holiday": date__holiday_map.get(date.strftime("%Y-%m-%d"), ""),
#         "data": [],
#         "count": 0,
#     }


def format_date(date: datetime.date) -> str:
    return date.strftime("%Y-%m-%d")


def between(
    start_date: datetime.date, end_date: datetime.date
) -> Generator[datetime.date, None, None]:
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)


def generate_blank_calendar(
    start_date: datetime.date, end_date: datetime.date
) -> Dict[str, dict]:
    calendar: Dict[str, dict] = {}
    for current_date in between(start_date, end_date):
        date_str = format_date(current_date)
        calendar[date_str] = {
            "date": current_date,
            "is_available": True,
            "data": [],
            "rules": [],
            "count": 0,
            "is_canceled": False,
        }
    return calendar
    # date__holiday_map: dict = parse_holiday_file(f"common/data/{year}.json")
    # # 初始化日期为该月的第一天
    # start_date = datetime.date(year, month, 1)
    # # 计算下一个月的第一天，处理越界到下一年下一月的情况
    # if month == 12:
    #     next_month_first_date = datetime.date(year + 1, 1, 1)
    # else:
    #     next_month_first_date = datetime.date(year, month + 1, 1)
    #
    # # 初始化一个空的结果列表
    # monthly_calendar = []
    #
    # # 当前日期从本月第一天开始
    # current_date = start_date
    #
    # # 补全上个月的日期
    # while current_date.isoweekday() != 1:
    #     current_date -= datetime.timedelta(days=1)
    #     monthly_calendar.insert(0, get_date_info(current_date, date__holiday_map))
    #
    # # 当前日期设置回本月第一天
    # current_date = start_date
    #
    # # 添加本月的日期
    # while current_date < next_month_first_date:
    #     monthly_calendar.append(get_date_info(current_date, date__holiday_map))
    #     current_date += datetime.timedelta(days=1)
    #
    # # 补全下个月的日期直到星期天, 并确保总数为42天（6*7）
    # while len(monthly_calendar) % 7 != 0 and len(monthly_calendar) < 42:
    #     monthly_calendar.append(get_date_info(current_date, date__holiday_map))
    #     current_date += datetime.timedelta(days=1)
    #
    # return {day["date"]: day for day in monthly_calendar}


def inject_training_class_to_calendar(
    blank_calendar, training_classes: QuerySet["TrainingClass"]
):
    # 培训班信息
    training_classes_info: List[dict] = [
        {
            "id": instance.id,
            "start_date": instance.start_date,
            "target_client_company_name": instance.target_client_company_name,
            "instructor_name": instance.instructor.username,
            "name": instance.name,
        }
        for instance in training_classes
    ]

    for programme in training_classes_info:
        start_date: datetime.date = programme.pop("start_date")
        formatted_start_date: str = start_date.strftime("%Y-%m-%d")
        formatted_next_date: str = (start_date + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

        # 更新当前日期的日历映射
        if formatted_start_date in blank_calendar:
            blank_calendar[formatted_start_date]["data"].append(programme)
            blank_calendar[formatted_start_date]["count"] += 1

        # 更新下一天的日历映射
        if formatted_next_date in blank_calendar:
            blank_calendar[formatted_next_date]["data"].append(programme)
            blank_calendar[formatted_next_date]["count"] += 1
