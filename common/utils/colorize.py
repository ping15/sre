import datetime
import logging
from functools import wraps

from colorama import Fore, init

init(autoreset=True)

logger = logging.getLogger(__name__)


def bold_and_underline(text):
    """字体加粗 + 下划线"""
    # ANSI escape sequences for bold and underline
    bold = '\033[1m'
    underline = '\033[4m'
    reset = '\033[0m'

    # Apply bold and underline
    result = f"{bold}{underline}{text}{reset}"

    return result


def task_decorator(func):
    """
    开始: 绿色
    执行过程: 蓝色
    结束: 黄色
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 开始
        start_time = datetime.datetime.now()
        print(Fore.GREEN + f"Task {bold_and_underline(func.__name__)}{Fore.GREEN} started at {start_time}")

        # 执行过程
        print(Fore.CYAN)
        result = func(*args, **kwargs)

        # 结束
        end_time = datetime.datetime.now()
        print(Fore.YELLOW + f"Task {bold_and_underline(func.__name__)}{Fore.YELLOW} "
                            f"finished at {end_time}, Duration: {end_time - start_time}")
        print(Fore.WHITE)

        return result

    return wrapper
