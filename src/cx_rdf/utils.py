# -*- coding: utf-8 -*-

"""Utilities for CX-RDF."""

from typing import Dict, Iterable, List, Tuple

import rdflib

from .constants import CX
from .typing import CxType

__all__ = [
    'iterate_aspect_fragments',
    'bind_cx_namespace',
]


def iterate_aspect_fragments(cx_json: CxType) -> Iterable[Tuple[str, List[Dict]]]:
    """Iterate over aspects and their entries.

    :param cx_json: A CX JSON object
    :return: A generator of pairs of aspect names and elements
    """
    for aspect in cx_json:
        for name, elements in aspect.items():
            yield name, elements


def bind_cx_namespace(graph: rdflib.Graph):
    """Bind the CX namespace to the RDFLib graph's namespace manager."""
    graph.namespace_manager.bind('cx', CX)
