import logging
import time
from functools import wraps
from typing import Dict

from django.db import connection

logger = logging.getLogger(__name__)


def reverse_dict(d: Dict[str, str]) -> Dict[str, str]:
    return {v: k for k, v in d.items()}


def query_debugger(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # 清除之前的查询
        connection.queries_log.clear()

        # 开始计时
        start_time = time.perf_counter()

        # 执行被装饰的函数
        result = func(*args, **kwargs)

        # 结束计时
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        # 查询数量
        query_count = len(connection.queries)

        # 打印或记录详细信息
        print(f"Function `{func.__name__}` executed in {elapsed_time:.2f}s")
        print(f"Total queries: {query_count}")
        for query in connection.queries:
            print(f"SQL: {query['sql']} | Time: {query['time']}")

        return result

    return inner


# def cache_representation(func)
