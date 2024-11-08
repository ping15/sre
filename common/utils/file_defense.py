import bleach

from common.utils import global_constants


def convert_resource_url(url: str) -> str:
    """防止资源恶意注入"""
    return url if global_constants.DOWNLOAD_URL in url else ""


def clean_text_file(content: str) -> str:
    """清洗文本文件内容"""
    return bleach.clean(content)
