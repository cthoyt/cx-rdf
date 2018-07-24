# -*- coding: utf-8 -*-

"""Type hints for CX-RDF."""

from typing import Dict, List

__all__ = [
    'CxType',
]

#: The type used for CX JSON
CxType = List[Dict[str, List[Dict]]]
