# -*- coding: utf-8 -*-

from typing import Dict, List

__all__ = [
    'CxType',
]

#: The type used for CX JSON
CxType = List[Dict[str, List[Dict]]]
