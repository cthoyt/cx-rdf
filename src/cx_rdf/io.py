# -*- coding: utf-8 -*-

from typing import Optional

import rdflib

from . import abstract_policy, aspect_policy, predicate_policy
from .typing import CxType

__all__ = [
    'cx_to_rdf_graph'
]

ALLOWED_POLICIES = ['aspect', 'abstract', 'predicate']


def cx_to_rdf_graph(cx_json: CxType, policy: Optional[str] = None) -> rdflib.Graph:
    """Export CX as RDF with the given policy.

    :param cx_json: CX JSON
    :param policy: Defaults to the 'predicate' policy. Can also use 'abstract' or 'aspect'
    """
    if policy is None:
        return predicate_policy.export(cx_json)

    if policy not in ALLOWED_POLICIES:
        ValueError('invalid policy given: {}. Use one of: {}'.format(policy, ', '.format(ALLOWED_POLICIES)))

    if policy == 'aspect':
        return aspect_policy.export(cx_json)

    if policy == 'abstract':
        return abstract_policy.export(cx_json)

    if policy == 'predicate':
        return predicate_policy.export(cx_json)
