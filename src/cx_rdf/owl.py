"""Functions to import OWL to CX"""

import json

from ndex2 import NiceCXNetwork
from owlready2 import EntityClass, Thing, get_ontology, Restriction

entities = {}


def ensure_node(cx: NiceCXNetwork, entity_class: EntityClass):
    try:
        name = EntityClass.get_name(entity_class)
    except:
        return

    node_id = cx.create_node(node_name=name)
    entities[entity_class] = node_id
    return node_id


def convert_owl(base_iri: str) -> NiceCXNetwork:
    onto = get_ontology(base_iri).load()

    cx = NiceCXNetwork()

    for entity_class in onto.classes():
        ensure_node(cx, entity_class)

    for entity_class in onto.classes():
        edge_source = ensure_node(cx, entity_class)

        if edge_source is None:
            raise ValueError('edge is none!')

        for super_class in entity_class.is_a:
            if super_class is Thing:
                continue

            if isinstance(super_class,Restriction):
                continue

            edge_target = ensure_node(cx, super_class)

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


if __name__ == '__main__':
    wine = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine'
    network = convert_owl(wine)
    print(json.dumps(network.to_cx(), indent=2))
