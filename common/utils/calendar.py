import datetime
from typing import Dict, Generator, List

from django.db.models import QuerySet

from apps.teaching_space.models import TrainingClass


def format_date(date: datetime.date) -> str:
    return date.strftime("%Y-%m-%d")


def between(start_date: datetime.date, end_date: datetime.date) -> Generator[datetime.date, None, None]:
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


def inject_training_class_to_calendar(blank_calendar, training_classes: QuerySet["TrainingClass"]):
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
