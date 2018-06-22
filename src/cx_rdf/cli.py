# -*- coding: utf-8 -*-

"""CLI for CX-RDF."""

import json
import os
import sys

import click
import ndex2

from .io import ALLOWED_POLICIES, cx_to_rdf_graph
from .owl import convert_owl

EXPORT_FORMATS = ['xml', 'n3', 'turtle', 'nt', 'pretty-xml', 'trix', 'trig', 'nquads']


@click.group()
def main():
    """Utilities for converting CX and RDF."""


@main.command()
@click.option('-i', '--file', type=click.File(), default=sys.stdin, help='Input CX file path. Defaults to STDIN')
@click.option('-o', '--destination', type=click.File('w'), default=sys.stdout,
              help='Output RDF file path. Defaults to STDOUT.')
@click.option('-p', '--policy', type=click.Choice(ALLOWED_POLICIES), help='RDF schema policy')
@click.option('-f', '--rdf-format', type=click.Choice(EXPORT_FORMATS), help='RDF output format')
def cx_to_rdf(file, destination, policy, rdf_format):
    """Convert CX to RDF."""
    cx_json = json.load(file)
    graph = cx_to_rdf_graph(cx_json, policy=policy)
    graph.serialize(destination=destination, format=rdf_format)


@main.command()
@click.argument('base_iri')
@click.option('-o', '--destination', type=click.File('w'), default=sys.stdout,
              help='Output CX file path. Defaults to STDOUT.')
@click.option('--indent', type=int, help='Pretty print JSON indent option')
@click.option('--ndex', is_flag=True,
              help='Enables upload to NDEx. NDEX_USERNAME and NDEX_PASSWORD must be set in the environment.')
def owl_to_cx(base_iri, destination, indent, ndex):
    """Download/load OWL then convert to CX."""
    cx = convert_owl(base_iri)

    if ndex:
        username = os.environ['NDEX_USERNAME']
        password = os.environ['NDEX_USERNAME']
        client = ndex2.Ndex2(username=username, password=password)
        uri = client.save_new_network(cx.to_cx())
        click.echo(uri.rsplit('/')[-1])

    else:
        json.dump(cx.to_cx(), destination, indent=indent)


if __name__ == '__main__':
    main()
