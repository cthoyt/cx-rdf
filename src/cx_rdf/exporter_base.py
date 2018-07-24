# -*- coding: utf-8 -*-

"""A base class for CX export policies."""

from abc import ABC, abstractmethod
import logging
from typing import Optional

from rdflib import BNode, Graph, Literal, RDF, RDFS
from rdflib.term import Node

from .constants import CX
from .typing import CxType
from .utils import bind_cx_namespace

__all__ = [
    'Exporter',
]

log = logging.getLogger(__name__)


class Exporter(ABC):
    """The base class for CX to RDF exporters."""

    policy = None

    def __init__(self, graph: Optional[Graph] = None):
        """Initialize the exporter with several caches."""
        self.id_node = {}
        self.id_edge = {}
        self.id_citation = {}
        self.id_support = {}

        self.graph = graph or Graph()
        bind_cx_namespace(self.graph)
        self.document = BNode()
        self._add_document(RDF.type, CX.network)

        if self.policy is None:
            raise TypeError(f'policy has not been set on class {self.__class__}')

        self._add_document(CX.policy, self.policy)

    def _add_label(self, s: Node, label: str):
        """Add a label to a node."""
        self.graph.add((s, RDFS.label, Literal(label)))

    def _add_document(self, p: Node, o: Node):
        """Add a predicate and object triple with the document as the subject."""
        self.graph.add((self.document, p, o))

    def ensure_node(self, node_id: int) -> BNode:
        """Get a node with a given identifier from CX if it exists, otherwise create a BNode for it."""
        node = self.id_node.get(node_id)
        if node is not None:
            return node

        node = self.id_node[node_id] = BNode()  # represents the node
        self.graph.add((node, RDF.type, CX.node))
        self.graph.add((node, CX.has_id, Literal(node_id)))
        self._add_document(CX.has_node, node)
        return node

    def ensure_edge(self, edge_id: int) -> BNode:
        """Get an edge with a given identifier from CX if it exists, otherwise create a BNode for it."""
        edge = self.id_edge.get(edge_id)
        if edge is not None:
            return edge

        edge = self.id_edge[edge_id] = BNode()
        self.graph.add((edge, RDF.type, CX.edge))
        self.graph.add((edge, CX.edge_has_id, Literal(edge_id)))
        self._add_document(CX.has_edge, edge)
        return edge

    def ensure_citation(self, citation_id: int) -> BNode:
        """Get a citation with a given identifier from CX if it exists, otherwise create a BNode for it."""
        citation = self.id_citation.get(citation_id)
        if citation is not None:
            return citation

        citation = self.id_citation[citation_id] = BNode()
        self.graph.add((citation, RDF.type, CX.citation))
        self.graph.add((citation, CX.citation_has_id, Literal(citation_id)))
        self._add_document(CX.has_citation, citation)
        return citation

    def ensure_support(self, support_id: int) -> BNode:
        """Get a support with a given identifier from CX if it exists, otherwise create a BNode for it."""
        support = self.id_support.get(support_id)
        if support is not None:
            return support

        support = self.id_support[support_id] = BNode()
        self.graph.add((support, RDF.type, CX.support))
        self.graph.add((support, CX.support_has_id, Literal(support_id)))
        self._add_document(CX.has_support, support)
        return support

    @abstractmethod
    def export(self, cx_json: CxType) -> Graph:
        """Convert a CX json to a RDFLib graph.

        :param cx_json: A CX JSON object
        """
        raise NotImplementedError
