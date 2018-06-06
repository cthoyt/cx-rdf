# -*- coding: utf-8 -*-

"""Functions for exporting CX to RDF."""

import logging

from rdflib import Graph

__all__ = [
    'export',
]

log = logging.getLogger(__name__)


def export(cx_json):
    """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

    :param list[dict] cx_json: A CX JSON object
    :return: An RDFLib graph
    :rtype: rdflib.Graph
    """
    graph = Graph()

    for element in cx_json:
        _add_element(element, graph)

    return graph


def _add_element(element, graph):
    """Add a CX group to the graph.

    :param dict element: An element of CX
    :param rdflib.Graph graph: An RDF graph.
    """
    log.info('graph: %s', graph)
    log.info('element: %s', element)
