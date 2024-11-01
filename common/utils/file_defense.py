import bleach

from common.utils import global_constants


def convert_resource_url(url: str) -> str:
    """防止资源恶意注入"""
    return url if global_constants.DOWNLOAD_URL in url else ""


def clean_text_file(content):
    """清洗文本文件内容"""
    return bleach.clean(content)


def scan_file(file):
    """假设这是一个扫描文件的函数"""
    # import os
    # import subprocess
    #
    # # 将文件保存到临时路径
    # temp_file_path = f'/tmp/{file.name}'
    # with open(temp_file_path, 'wb') as temp_file:
    #     for chunk in file.chunks():
    #         temp_file.write(chunk)
    #
    # # 调用ClamAV进行扫描
    # try:
    #     result = subprocess.run(['clamscan', temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     output = result.stdout.decode()
    #
    #     # 检查扫描结果
    #     if "Infected files: 0" in output:
    #         is_safe = True
    #     else:
    #         is_safe = False
    # finally:
    #     # 清理临时文件
    #     os.remove(temp_file_path)
    #
    # return is_safe
