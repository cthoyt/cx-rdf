# -*- coding: utf-8 -*-

"""Post-processing tools for CX-RDF."""

import itertools as itt
from collections import defaultdict

from rdflib import Graph

from .constants import CX

ALIAS_EQUIVALENT = CX.alias_equivalent


def match_aliased(graph: Graph):
    """Find all aliased nodes and add an equivalence relation between them.

    :param graph: An RDFLib graph
    """
    cache = defaultdict(set)

    for sub, obj in graph.subject_objects(CX.node_has_alias):
        cache[obj].add(sub)

    for alias, refs in cache.items():
        for x, y in itt.product(refs, repeat=2):
            graph.add((x, ALIAS_EQUIVALENT, y))
            graph.add((y, ALIAS_EQUIVALENT, x))
