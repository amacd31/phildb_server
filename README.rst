PhilDB Server
=============

|PYPI Version| |PYPI Python versions| |PYPI License|

PhilDB server, for HTTP access to a `PhilDB
<https://github.com/amacd31/phildb>`_ instance.

Dependencies
------------

Requires Python 2.7 or Python 3.4 or greater.

Installation
------------

PhilDB server is pip installable.

The latest stable version can be installed from pypi with::

    pip install phildb-server

The latest development version can be installed from github with::

    pip install git+https://github.com/amacd31/phildb_server.git@dev

Usage
=====

Start a PhilDB using a specified PhilDB instance:

::

    phildb-server phildb_directory

List help options:

::

    phildb-server --help

.. |PYPI Version| image:: https://img.shields.io/pypi/v/phildb-server.svg
    :target: https://pypi.python.org/pypi/PhilDB

.. |PYPI Python versions| image:: https://img.shields.io/pypi/pyversions/phildb-server.svg
    :target: https://pypi.python.org/pypi/PhilDB-Server

.. |PYPI License| image:: https://img.shields.io/pypi/l/phildb-server.svg
    :target: https://github.com/amacd31/phildb-server/blob/master/LICENSE
