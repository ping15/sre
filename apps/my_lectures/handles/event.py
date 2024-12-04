import datetime
from datetime import date
from typing import Dict, List, Optional

from django.db.models import QuerySet
from rest_framework.exceptions import ParseError

from apps.platform_management.models import Event, Instructor
from apps.teaching_space.models import TrainingClass
from common.utils.calendar import between, format_date, generate_blank_calendar


class EventHandler:
    @classmethod
    def build_calendars(cls, events: QuerySet["Event"], start_date: date, end_date: date) -> List[dict]:
        """
        构建日程
        """
        blank_calendar: Dict[str, dict] = generate_blank_calendar(start_date, end_date)

        # events = events.filter(end_date__gte=start_date, start_date__lt=end_date).order_by("type")

        for event in events:
            event_start_date, event_end_date = event.start_date, event.end_date
            marking_start_date = max(start_date, event_start_date)

            # 如果未设置结束时间，以传入的结束时间作为最终的结束时间
            if not event_end_date:
                marking_end_date = end_date
            else:
                marking_end_date = min(end_date, event_end_date)

            if marking_start_date > marking_end_date:
                continue

            # 培训班排课
            if event.event_type == Event.EventType.CLASS_SCHEDULE.value:
                blank_calendar[format_date(marking_start_date)]["count"] += 1
                blank_calendar[format_date(marking_start_date)]["data"].append(cls.build_event_data(event))

            # 取消单日不可用时间
            elif event.event_type == Event.EventType.CANCEL_UNAVAILABILITY.value:
                assert event_start_date == event_end_date
                cls.marking_canceled(blank_calendar, marking_start_date, marking_end_date)

            # 登记一次性不可用时间规则和周期性不可用时间规则
            elif event.event_type in [
                Event.EventType.ONE_TIME_UNAVAILABILITY, Event.EventType.RECURRING_UNAVAILABILITY
            ]:
                cls.marking_unavailable(blank_calendar, event, marking_start_date, marking_end_date)

        blank_calendar = {
            current_date: calendar_info
            for current_date, calendar_info in blank_calendar.items()
            if calendar_info["data"] or calendar_info["rules"] or not calendar_info["is_available"]
        }

        # 将字典转换为列表并按 start_date 排序
        return sorted(blank_calendar.values(), key=lambda x: x["date"])

    @classmethod
    def build_event_data(cls, event: Event) -> Dict:
        """
        构建event数据
        """
        if event.event_type == Event.EventType.CLASS_SCHEDULE.value:
            training_class: TrainingClass = event.training_class
            return {
                "id": training_class.id,
                "start_date": training_class.start_date,
                "end_date": training_class.start_date + datetime.timedelta(days=1),
                "target_client_company_name": training_class.target_client_company_name,
                "instructor_name": training_class.instructor_name,
                "name": training_class.name,
            }

        return {
            "id": event.id,
            "event_type": event.event_type,
            "freq_type": event.freq_type,
            "freq_interval": event.freq_interval,
            "start_date": event.start_date,
            "end_date": event.end_date,
        }

    @classmethod
    def marking_unavailable(cls, blank_calendar: Dict[str, dict], event: Event, start_date: date, end_date: date):
        """
        标记不可用时间
        """
        event_type = event.event_type
        for current_date in between(start_date, end_date):
            if blank_calendar[format_date(current_date)]["is_canceled"]:
                continue

            if event_type == Event.EventType.ONE_TIME_UNAVAILABILITY.value:
                cls._marking_unavailable(blank_calendar, event, current_date)

            elif event_type == Event.EventType.RECURRING_UNAVAILABILITY.value:
                if cls.is_current_date_in_rule(current_date, event):
                    cls._marking_unavailable(blank_calendar, event, current_date)

    @classmethod
    def _marking_unavailable(cls, blank_calendar: Dict[str, dict], event: Event, current_date: date):
        blank_calendar[format_date(current_date)]["is_available"] = False
        blank_calendar[format_date(current_date)]["rules"].append(cls.build_event_data(event))

    @classmethod
    def marking_canceled(cls, blank_calendar: Dict[str, dict], start_date: date, end_date: date):
        """
        取消单日不可用时间
        """
        for current_date in between(start_date, end_date):
            blank_calendar[format_date(current_date)]["is_canceled"] = True
            blank_calendar[format_date(current_date)]["is_available"] = True

    @classmethod
    def is_event_conflict_to_rule(cls, event: Event, rule: Event) -> bool:
        """
        判断当前事件是否与规则冲突
        """
        for current_date in between(event.start_date, event.end_date):
            if not cls.is_current_date_in_range(current_date, rule.start_date, rule.end_date):
                continue

            if cls.is_current_date_in_rule(current_date, rule):
                return True

        return False

    @classmethod
    def is_current_date_in_range(cls, current_date: date, start_date: date, end_date: Optional[date]) -> bool:
        """
        检查 current_date 是否在 start_date 和 end_date 之间。
        如果 end_date 是 None，表示没有结束日期，范围延续到无穷远。
        """
        if end_date is None:
            return current_date >= start_date
        return start_date <= current_date <= end_date

    @classmethod
    def is_current_date_in_rule(cls, current_date: date, rule: Event) -> bool:
        """
        检查 current_date 是否在规则范围内
        """
        assert rule.event_type in [Event.EventType.ONE_TIME_UNAVAILABILITY, Event.EventType.RECURRING_UNAVAILABILITY]

        # 不在时间范围内，规则无效
        if not cls.is_current_date_in_range(current_date, rule.start_date, rule.end_date):
            return False

        if rule.event_type == Event.EventType.ONE_TIME_UNAVAILABILITY.value:
            return True

        elif rule.freq_type == Event.FreqType.WEEKLY and current_date.isoweekday() in rule.freq_interval:
            return True

        elif rule.freq_type == Event.FreqType.MONTHLY and current_date.day in rule.freq_interval:
            return True

        elif rule.freq_type == Event.FreqType.BIWEEKLY:
            delta_days = (current_date - rule.start_date).days
            if (delta_days // 7) % 2 == 0 and current_date.isoweekday() in rule.freq_interval:
                return True

        return False

    @classmethod
    def is_current_date_in_cancel_events(cls, current_date: date, cancel_dates: Optional[List[date]] = None) -> bool:
        """
        检查 current_date 是否在取消不可用时间范围内
        """
        cancel_dates: List[date] = cancel_dates or Event.objects.filter(
            event_type=Event.EventType.CANCEL_UNAVAILABILITY).values_list("start_date", flat=True)

        return current_date in cancel_dates

    @classmethod
    def create_event(
        cls,
        event_type: str,
        freq_interval: Optional[List] = None,
        freq_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        instructor: Optional[Instructor] = None,
        training_class: Optional[TrainingClass] = None,
    ) -> Event:
        assert instructor or training_class, "instructor 或者 training_class 必须有一个，否则没有讲师信息"
        assert start_date or training_class, "start_date 或者 training_class 必须有一个，否则没有开始时间"
        freq_interval = freq_interval or []
        if training_class:
            start_date, end_date = training_class.start_date, training_class.start_date + datetime.timedelta(days=1)
            event_type = Event.EventType.CLASS_SCHEDULE.value
            instructor = training_class.instructor

        new_event: Event = Event(
            event_type=event_type,
            freq_type=freq_type,
            freq_interval=freq_interval,
            start_date=start_date,
            end_date=end_date,
            instructor=instructor,
            training_class=training_class,
        )

        if new_event.event_type in [Event.EventType.ONE_TIME_UNAVAILABILITY, Event.EventType.RECURRING_UNAVAILABILITY]:
            rule = new_event

            # 如果与培训班日程冲突，直接返回不创建
            for event in instructor.events.filter(event_type=Event.EventType.CLASS_SCHEDULE):
                if cls.is_event_conflict_to_rule(event, rule):
                    raise ParseError("该规则与已有的培训班日程存在冲突")

            # 如果与讲师参与广告报名冲突，直接返回不创建

            # [取消单日不可用时间]如果在规则内，则清除该类型的事件
            for event in instructor.events.filter(event_type=Event.EventType.CANCEL_UNAVAILABILITY):
                if cls.is_event_conflict_to_rule(event, rule):
                    event.delete()

        elif new_event.event_type == Event.EventType.CLASS_SCHEDULE.value:
            for event in instructor.events.filter(event_type=Event.EventType.CLASS_SCHEDULE):
                if all([
                    cls.is_current_date_in_range(current_date, event.start_date, event.end_date)
                    for current_date in between(new_event.start_date, new_event.end_date)
                ]):
                    raise ParseError("该培训班与已有的培训班排期存在冲突")

            # 该讲师所有[取消单日不可用时间]
            cancel_dates: List[date] = instructor.events.filter(
                event_type=Event.EventType.CANCEL_UNAVAILABILITY).values_list("start_date", flat=True)

            # [取消单日不可用时间]如果覆盖培训班日程，则不受规则约束
            if not all([current_date in cancel_dates for current_date in between(start_date, end_date)]):
                # 如果该讲师的不可用时间和培训班日程冲突，直接返回不创建
                for rule in instructor.events.filter(event_type__in=Event.EventType.rule_types):
                    if cls.is_event_conflict_to_rule(new_event, rule):
                        raise ParseError("该培训班与已有的规则存在冲突")

        new_event.save()

        return new_event

    @classmethod
    def is_current_date_usable(
        cls,
        current_date: date,
        instructor: Instructor,
        without_training_class: bool = False,
        without_rule: bool = False,
        without_cancel_event: bool = False,
    ) -> bool:
        for training_event in instructor.events.filter(event_type=Event.EventType.CLASS_SCHEDULE):
            if without_training_class:
                break

            # 判断是否在培训班日程范围内
            if cls.is_current_date_in_range(current_date, training_event.start_date, training_event.end_date):
                return False

        for cancel_event in instructor.events.filter(event_type=Event.EventType.CANCEL_UNAVAILABILITY):
            if without_cancel_event:
                break

            # 判断是否在取消不可用时间范围内
            if cls.is_current_date_in_cancel_events(current_date, [cancel_event.start_date]):
                return True

        for event in instructor.events.filter(event_type__in=Event.EventType.rule_types):
            if without_rule:
                break

            # 判断是否在规则范围内
            if cls.is_current_date_in_rule(current_date, event):
                return False

        return True

    @classmethod
    def is_range_date_usable(
        cls,
        start_date: date,
        end_date: date,
        instructor: Instructor,
        without_training_class: bool = False,
        without_rule: bool = False,
        without_cancel_event: bool = False,
    ) -> bool:
        for current_date in between(start_date, end_date):
            if not cls.is_current_date_usable(
                current_date=current_date,
                instructor=instructor,
                without_training_class=without_training_class,
                without_rule=without_rule,
                without_cancel_event=without_cancel_event,
            ):
                return False

        return True

    @classmethod
    def is_instructor_idle(cls, instructor: Instructor, start_date: date, end_date: date) -> bool:
        """在期间内该讲师是否都有空闲时间"""
        rule_events: QuerySet["Event"] = instructor.events.filter(event_type__in=Event.EventType.rule_types)
        cancel_days: List[datetime.date] = instructor.events.filter(
            event_type=Event.EventType.CANCEL_UNAVAILABILITY).values_list("start_date", flat=True)
        training_events: QuerySet["Event"] = instructor.events.filter(event_type=Event.EventType.CLASS_SCHEDULE)

        # 如果周期内某一天不可用，则整个周期不可用
        for day in between(start_date, end_date):
            # 如果该天有培训班日程，则该天不可用
            for event in training_events:
                if cls.is_current_date_in_range(day, event.start_date, event.end_date):
                    return False

            # [取消单日不可用时间]优先级高于[规则]，如果该天在[取消单日不可用时间]范围内，则该天可用
            if cls.is_current_date_in_cancel_events(day, cancel_days):
                continue

            # 如果该天在[规则]，则该天不可用
            for rule in rule_events:
                if cls.is_current_date_in_rule(day, rule):
                    return False

        return True
