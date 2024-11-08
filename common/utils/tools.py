import logging
import time
from functools import wraps
from typing import Dict

from django.db import connection

logger = logging.getLogger(__name__)


def reverse_dict(d: Dict[str, str]) -> Dict[str, str]:
    """字典反转"""
    return {v: k for k, v in d.items()}


def query_debugger(func):
    """查看数据库查询次数和执行时间"""
    @wraps(func)
    def inner(*args, **kwargs):
        # 清除之前的查询
        connection.queries_log.clear()

        # 开始计时
        start_time = time.perf_counter()

        result = func(*args, **kwargs)

        # 打印或记录详细信息
        print(f"函数 `{func.__name__}` 执行时间 {time.perf_counter() - start_time:.2f}s")
        print(f"全部DB查询次数: {len(connection.queries)}")
        for query in connection.queries:
            print(f"SQL: {query['sql']} | Time: {query['time']}")

        return result

    return inner
