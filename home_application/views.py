# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
import os

from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    """
    首页
    """
    context = {
        "BK_API_HOST": os.environ.get("BK_API_HOST", ""),
        "BK_EXAM_HOST": os.environ.get("BK_EXAM_HOST", ""),
    }
    return render(request, "home_application/index.html", context=context)


def view_error_log(request):
    try:
        with open('error_log.json', 'r') as f:
            errors = json.load(f)  # 直接加载整个 JSON 对象
    except FileNotFoundError:
        errors = {}
    except json.JSONDecodeError:
        errors = {}

    return JsonResponse(errors, safe=False)
