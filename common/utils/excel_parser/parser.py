from typing import Any, Dict, List
from urllib.parse import unquote

import pandas as pd


def excel_to_list(
    file_path: str, mapping: Dict[str, Dict[str, str]]
) -> List[Dict[str, str]]:
    df = pd.read_excel(open(unquote(file_path)[1:], "rb"))
    field_name__field_type: Dict[str, str] = {
        column_mapping["value"]: column_mapping["type"]
        for excel_column, column_mapping in mapping.items()
    }
    excel_column__field_name: Dict[str, str] = {
        column: column_mapping["value"] for column, column_mapping in mapping.items()
    }
    df = df.rename(columns=excel_column__field_name)
    datas: List[Dict[str, str]] = df.to_dict(orient="records")
    datas = [_convert_data(data, field_name__field_type) for data in datas]
    return datas


def _convert_data(data: Dict[str, Any], field_name__field_type: Dict[str, str]) -> Dict[str, str]:
    for field_name, field_value in data.copy().items():
        if field_name__field_type[field_name] == list:
            data[field_name] = str(field_value).split(",")
        elif field_name__field_type[field_name] == str:
            data[field_name] = str(field_value)

    return data
