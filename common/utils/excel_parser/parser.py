from typing import Dict, List, Union

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile


def excel_to_list(
    file_path: Union[str, InMemoryUploadedFile], mapping: Dict[str, str]
) -> List[Dict[str, str]]:
    df = pd.read_excel(file_path)
    df = df.rename(columns=mapping)
    return df.to_dict(orient="records")
