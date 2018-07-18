# -*- coding: utf-8 -*-

"""Functions to import OWL to CX."""

from owlready2 import EntityClass, Restriction, Thing, get_ontology

from ndex2 import NiceCXNetwork


def ensure_node(cx: NiceCXNetwork, entities, entity_class: EntityClass):
    try:
        name = EntityClass.get_name(entity_class)
    except:
        return

    node_id = cx.create_node(node_name=name)

    try:
        label = entity_class.label.first()
        if label:
            cx.add_node_attribute(property_of=node_id, name='l', values=label)
    except:
        pass

    entities[entity_class] = node_id
    return node_id


def convert_owl(base_iri: str) -> NiceCXNetwork:
    """Serialize an OWL ontology in CX.

    :param base_iri: The IRI of an ontology to download with :py:mod:`owlready2`
    :return: A nice CX network
    """
    onto = get_ontology(base_iri).load()

    cx = NiceCXNetwork()
    entities = {}

    for entity_class in onto.classes():
        edge_source = ensure_node(cx, entities, entity_class)

        if edge_source is None:
            raise ValueError('edge is none!')

        for super_class in entity_class.is_a:
            if super_class is Thing:
                continue

            if isinstance(super_class, Restriction):
                continue

            edge_target = ensure_node(cx, entities, super_class)

            if edge_target is None:
                raise ValueError('Edge taret is none for {} ({})'.format(super_class, super_class.__class__))

            cx.create_edge(
                edge_source=edge_source,
                edge_target=edge_target,
                edge_interaction='subClassOf',
            )

            # TODO add more attributes/properties?

        for i in entity_class.instances():
            print('instance: %s', i)

    cx.update_consistency_group()

    return cx
