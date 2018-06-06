# -*- coding: utf-8 -*-

"""CLI for CX-RDF."""

import json
import sys

import click

from .export import export

EXPORT_FORMATS = ['xml', 'n3', 'turtle', 'nt', 'pretty-xml', 'trix', 'trig', 'nquads']


@click.group()
def main():
    """Utilities for converting CX and RDF."""


@main.command()
@click.option('-i', '--file', type=click.File(), default=sys.stdin)
@click.option('-o', '--destination', type=click.File('w'), default=sys.stdout)
@click.option('-f', '--rdf-format', choices=EXPORT_FORMATS)
def cx_to_rdf(file, destination, rdf_format):
    """Convert CX to RDF."""
    cx_json = json.load(file)
    graph = export(cx_json)
    graph.serialize(destination=destination, format=rdf_format)


if __name__ == '__main__':
    main()
