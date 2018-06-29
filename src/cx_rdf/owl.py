"""Functions to import OWL to CX"""

import json
import sys
from owlready2 import EntityClass, Restriction, Thing, get_ontology

from ndex2 import NiceCXNetwork

entities = {}


def ensure_node(cx: NiceCXNetwork, entity_class: EntityClass):
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

    for entity_class in onto.classes():
        edge_source = ensure_node(cx, entity_class)

        if edge_source is None:
            raise ValueError('edge is none!')

        for super_class in entity_class.is_a:
            if super_class is Thing:
                continue

            if isinstance(super_class, Restriction):
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
    import os
    import sys

    wine_iri = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine'
    wine_network = convert_owl(wine_iri)
    wine_network.set_name('Wine!')
    wine_network.add_network_attribute(name='iri', values=wine_iri)
    wine_cx = wine_network.to_cx()
    wine_cx.append({"status": [{"error": "", "success": True}]})
    with open('wine.cx', 'w') as file:
        json.dump(wine_cx, file, indent=2)

    wine_network.upload_to(None, os.environ['NDEX_USERNAME'], os.environ['NDEX_PASSWORD'])

    gene_ontology_iri = 'http://purl.obolibrary.org/obo/go/releases/2018-06-28/go.owl'
    gene_ontology_network = convert_owl(gene_ontology_iri)
    gene_ontology_network.set_name('Gene Ontology')
    gene_ontology_cx = gene_ontology_network.to_cx()
    gene_ontology_cx.append({"status": [{"error": "", "success": True}]})

    gene_ontology_network.upload_to(None, os.environ['NDEX_USERNAME'], os.environ['NDEX_PASSWORD'])

    with open('go.cx', 'w') as file:
        json.dump(gene_ontology_cx, file, indent=2)
