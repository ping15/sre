import datetime
import json
from typing import Dict


def parse_holiday_file(holiday_filepath: str) -> dict:
    with open(holiday_filepath, "r", encoding="utf-8") as f:
        days: list = json.load(f).get("days", [])

    seen: set = set()
    unique_days: list = []
    for day in days:
        if day["name"] not in seen:
            unique_days.append(day)
            seen.add(day["name"])

    return {day["date"]: day["name"] for day in unique_days}


def get_date_info(date: datetime.date, date__holiday_map: dict):
    return {
        "date": date.strftime("%Y-%m-%d"),
        "is_available": True,
        "holiday": date__holiday_map.get(date.strftime("%Y-%m-%d"), ""),
        "data": [],
        "count": 0,
    }


def generate_calendar(year: int, month: int) -> Dict[str, dict]:
    date__holiday_map: dict = parse_holiday_file(f"common/data/{year}.json")
    # 初始化日期为该月的第一天
    start_date = datetime.date(year, month, 1)
    # 计算下一个月的第一天，处理越界到下一年下一月的情况
    if month == 12:
        next_month_first_date = datetime.date(year + 1, 1, 1)
    else:
        next_month_first_date = datetime.date(year, month + 1, 1)

    # 初始化一个空的结果列表
    monthly_calendar = []

    # 当前日期从本月第一天开始
    current_date = start_date

    # 补全上个月的日期
    while current_date.isoweekday() != 1:
        current_date -= datetime.timedelta(days=1)
        monthly_calendar.insert(0, get_date_info(current_date, date__holiday_map))

    # 当前日期设置回本月第一天
    current_date = start_date

    # 添加本月的日期
    while current_date < next_month_first_date:
        monthly_calendar.append(get_date_info(current_date, date__holiday_map))
        current_date += datetime.timedelta(days=1)

    # 补全下个月的日期直到星期天, 并确保总数为42天（6*7）
    while len(monthly_calendar) % 7 != 0 and len(monthly_calendar) < 42:
        monthly_calendar.append(get_date_info(current_date, date__holiday_map))
        current_date += datetime.timedelta(days=1)

    return {day["date"]: day for day in monthly_calendar}