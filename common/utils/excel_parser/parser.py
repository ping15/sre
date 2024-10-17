from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def excel_to_list(contents: bytes, mapping: Dict[str, Dict[str, str]]) -> Tuple[List[Dict[str, str]], Optional[str]]:
    err_msg = None
    df = pd.read_excel(contents)

    # 字段名 -> 字段类型
    field_name__field_type: Dict[str, str] = {
        column_mapping["value"]: column_mapping["type"]
        for excel_column, column_mapping in mapping.items()
    }

    # excel表头 -> 字段名
    excel_column__field_name: Dict[str, str] = {
        column: column_mapping["value"] for column, column_mapping in mapping.items()
    }

    # 将df中excel表头进行映射
    df = df.rename(columns=excel_column__field_name)

    datas: List[Dict[str, str]] = df.to_dict(orient="records")

    # 类型转换，df拿到的数据都为str
    datas = [_convert_data(data, field_name__field_type) for data in datas]
    if len(datas) > 0 and not datas[0]:
        err_msg = "Excel模板错误"

    return datas, err_msg


def _convert_data(data: Dict[str, Any], field_name__field_type: Dict[str, str]) -> Dict[str, str]:
    for field_name, field_value in data.copy().items():
        if field_name not in field_name__field_type:
            return {}

        if field_name__field_type[field_name] == list:
            data[field_name] = str(field_value).split(",")
        elif field_name__field_type[field_name] == str:
            data[field_name] = str(field_value)

    return data
