CX-RDF
======
A utility for converting CX to RDF.

Installation
------------
This module has not yet been pushed to PyPI. It can be downloaded and installed from GitHub using Python36.

.. code-block:: sh

    $ git clone https://github.com/cthoyt/cx-rdf.git
    $ cd cx-rdf
    $ python3 -m pip install -e .

Command Line Usage
------------------
The setup.py installs two commands:

``cx_to_rdf`` converts CX documents to RDF using one of three policies:

- abstract: RDF is used to represent CX itself, and does not take intuition from the content of CX. This is verbose,
  but most extensible
- aspect: Each aspect is converted individually with some knowledge of the biological meaning of each
- predicate: RDF is produced that captures the schema of networks most closely

``owl_to_cx`` is a rudimentary OWL to CX converter that captures ``subClassOf`` relationships.
