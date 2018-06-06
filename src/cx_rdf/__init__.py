# -*- coding: utf-8 -*-

"""A utility for converting CX to RDF.

Installation
------------
CX-RDF can be installed from the latest code on `GitHub <https://github.com/cthoyt/cx-rdf>`_ with:

.. code-block:: sh

   $ python3 -m pip install git+https://github.com/cthoyt/cx-rdf.git

Command Line Usage
------------------
CX-RDF installs a command line utility for converting a CX file to RDF. Example usage:

.. code-block:: sh

   $ cat my_network.cx | cx_to_rdf > my_network.xml

The ``-f`` option can be used to specify the format RDFLib uses to serialize. It defaults to
``xml``, but other formats like ``turtle`` are often preferred.
"""

from .export import export

__all__ = [
    'export',
]

__version__ = '0.0.1-dev'

__title__ = 'cx_rdf'
__description__ = 'A utility for converting CX to RDF'
__url__ = 'https://github.com/cthoyt/cx-rdf'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2018 Charles Tapley Hoyt'
