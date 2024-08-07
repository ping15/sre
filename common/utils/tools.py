from typing import Dict


def reverse_dict(d: Dict[str, str]) -> Dict[str, str]:
    return {k: v for k, v in d.items()}
