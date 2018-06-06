# -*- coding: utf-8 -*-

"""Functions for exporting CX to RDF."""

import logging

from rdflib import BNode, Graph, Literal, RDF, RDFS

from .constants import CX

__all__ = [
    'export_abstract',
]

log = logging.getLogger(__name__)


def export_abstract(cx_json):
    """Convert a CX JSON object to an RDFLib :class:`rdflib.Graph`.

    This policy for serializing CX to RDF is the most general, and only manages to encode the structure of a CX
    document in RDF. It has little semantic meaning.

    :param list[dict] cx_json: A CX JSON object
    :return: An RDFLib graph
    :rtype: rdflib.Graph
    """
    graph = Graph()

    document = BNode()
    graph.add((document, RDF.type, CX.cx))

    aspects = {}

    for element in cx_json:
        for aspect_name, entries in element.items():
            aspect = aspects.get(aspect_name)
            if aspect is None:
                aspect = BNode()
                graph.add((aspect, RDF.type, CX.aspect))
                graph.add((document, CX.has_aspect, aspect))

                graph.add((aspect, RDFS.label, Literal(aspect_name)))

                aspects[aspect_name] = aspect

            for entry_dict in entries:
                entry = BNode()
                graph.add((entry, RDF.type, CX.entry))
                graph.add((aspect, CX.has_entry, entry))

                for k, v in entry_dict.items():
                    attribute = BNode()
                    graph.add((attribute, RDF.type, CX.attribute))
                    graph.add((entry, CX.has_attribute, attribute))

                    graph.add((attribute, CX.has_key, Literal(k)))

                    # need to handle different types here
                    graph.add((attribute, CX.has_value, Literal(v)))

    return graph
