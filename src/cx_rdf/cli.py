# -*- coding: utf-8 -*-

"""CLI for CX-RDF."""

import json
import os
import sys

import click
import ndex2

from .io import cx_to_rdf_graph
from .owl import convert_owl

EXPORT_FORMATS = ['xml', 'n3', 'turtle', 'nt', 'pretty-xml', 'trix', 'trig', 'nquads']


@click.group()
def main():
    """Utilities for converting CX and RDF."""


@main.command()
@click.option('-i', '--file', type=click.File(), default=sys.stdin)
@click.option('-o', '--destination', type=click.File('w'), default=sys.stdout)
@click.option('-p', '--policy', help='RDF schema policy')
@click.option('-f', '--rdf-format', type=click.Choice(EXPORT_FORMATS))
def cx_to_rdf(file, destination, policy, rdf_format):
    """Convert CX to RDF."""
    cx_json = json.load(file)
    graph = cx_to_rdf_graph(cx_json, policy=policy)
    graph.serialize(destination=destination, format=rdf_format)


@main.command()
@click.argument('base_iri')
@click.option('-o', '--destination', type=click.File('w'), default=sys.stdout)
@click.option('--indent', type=int)
@click.option('--ndex', is_flag=True)
def owl_to_cx(base_iri, destination, indent, ndex):
    """Download/load OWL then convert to CX"""
    cx = convert_owl(base_iri)

    if ndex:
        username = os.environ.get('NDEX_USERNAME')
        password = os.environ.get('NDEX_USERNAME')
        client = ndex2.Ndex2(username=username, password=password)
        uri = client.save_new_network(cx.to_cx())
        click.echo(uri.rsplit('/')[-1])

    else:
        json.dump(cx.to_cx(), destination, indent=indent)


if __name__ == '__main__':
    main()
