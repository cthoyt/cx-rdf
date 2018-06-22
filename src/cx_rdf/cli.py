# -*- coding: utf-8 -*-

"""CLI for CX-RDF."""

import json
import sys

import click

from .io import cx_to_rdf_graph

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


if __name__ == '__main__':
    main()
