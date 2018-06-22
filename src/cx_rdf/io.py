# -*- coding: utf-8 -*-

import rdflib
from typing import Optional

from . import abstract_policy, aspect_policy, predicate_policy

__all__ = [
    'cx_to_rdf_graph'
]

ALLOWED_POLICIES = ['aspect', 'abstract', 'predicate']


def cx_to_rdf_graph(cx_json, policy: Optional[str] = None) -> rdflib.Graph:
    """Export CX as RDF with the given policy.

    :param cx_json:
    :param policy: Defaults to the 'aspect' policy. Can also use 'abstract' or 'predicate'
    """
    if policy is None:
        return aspect_policy.export(cx_json)

    if policy not in ALLOWED_POLICIES:
        ValueError('invalid policy given: {}. Use one of: {}'.format(policy, ', '.format(ALLOWED_POLICIES)))

    if policy == 'aspect':
        return aspect_policy.export(cx_json)

    if policy == 'abstract':
        return abstract_policy.export(cx_json)

    if policy == 'predicate':
        return predicate_policy.export(cx_json)
