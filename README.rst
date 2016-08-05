depman
======

.. image:: https://travis-ci.org/mbodenhamer/depman.svg?branch=master
    :target: https://travis-ci.org/mbodenhamer/depman
    
.. image:: https://img.shields.io/coveralls/mbodenhamer/depman.svg
    :target: https://coveralls.io/r/mbodenhamer/depman

.. image:: https://readthedocs.org/projects/depman/badge/?version=latest
    :target: http://depman.readthedocs.org/en/latest/?badge=latest

A lightweight dependency manager for managing project dependencies in multiple contexts. The use case driving development is that of distinguishing between development, testing, and production dependencies in a simple and unified way. However, the application is general purpose and can be used in any project requiring the management of dependencies in multiple contexts.

Currently, only dependencies resolved via ``apt-get`` and ``pip`` are supported.  However, support for other dependency types is planned for future releases (see `Future Features`_ for more details).

Installation
------------
::

    $ pip install -U depman


Usage
-----
::

    usage: depman [-h] [-f <depfile>] <command> [<context>]

    A lightweight dependency manager.

    positional arguments:
      <command>             'satisfy' satisfies the dependencies specified in
			    <depfile>. 'validate' only validates <depfile> and
			    does not perform any system operations
      <context>             The dependency context to perform <command> on

    optional arguments:
      -h, --help            show this help message and exit
      -f <depfile>, --depfile <depfile>
			    The requirements file to load

If not supplied, ``<depfile>`` and ``<context>`` default to ``requirements.yml`` and ``all``, respectively.

Example(s)
----------

Suppose you have the following ``requirements.yml`` in your current working directory::

    includes:
      dev:
	- test

    dev:
      apt:
	- libxml2-dev
	- libxslt1-dev
      pip:
	- lxml
	- Sphinx

    test:
      pip:
	- nose
	- coverage

    prod:
      pip:
	- gevent:
	    version: 1.0.2
	- texttable
	- syn:
	    always_upgrade: yes

This file specifies three dependency contexts: ``dev``, ``test``, ``prod``.  In general, any top-level key in ``requirements.yml`` specifies a dependency context.  The one exception to this rule is ``includes``, which defines inclusion relationships between contexts.  In this example, the ``dev`` context includes the ``test`` context.  As such, when ``depman satisfy test`` is run at the command line, ``depman`` will invoke ``pip`` to install ``nose`` and ``coverage``, if they do not exist on the system.  On the other hand, when ``depman satisfy dev`` is run at the command line, ``depman`` will first invoke ``apt-get`` to install ``libxml1-dev`` and ``libxslt1-dev`` and then invoke ``pip`` to install ``lxml``, ``Sphinx``, ``nose``, and ``coverage`` (in general, ``apt`` dependencies are processed before ``pip`` dependencies).  Because ``test`` is "included" in ``dev``, its dependencies are processed whenever ``dev`` is processed.
    
``depman`` also accepts the special context ``all`` as a valid command line parameter.  Running ``depman satisfy all`` causes ``depman`` to satisfy the dependencies in all of the defined dependency contexts.  In this example, it would cause ``depman`` to satisfy the dependencies for ``dev``, ``test``, and ``prod``.  Running ``depman satisfy`` is equivalent to running ``depman satisfy all``.

Currently, only two dependency types are supported in any context: ``apt`` and ``pip``.  However, support for other dependency types is planned for future releases (see `Future Features`_ for more details).
    
Dependencies are specified in each context under each dependency type (i.e. ``apt`` or ``pip``) as YAML list elements.  If the element is a string, the dependency in question will be treated as satisfied if some version of the package denoted by the string exists on the system.  For more detailed dependency requirements, the name of the package can be listed as the key to a YAML dictionary of dependency options.  This can be seen, for example, in the ``gevent`` dependency, in which a minimum version ``1.0.2`` is specified as a requirement.  Additionally, the ``syn`` package contains the ``always_upgrade`` option, which causes ``depman`` to always attempt to upgrade the package, regardless of the current version installed.

In version 0.1, versioning features are only available for ``pip`` dependencies, but versioning options will be added to other dependency types in future releases.

.. _Future Features:

Future Features
---------------

The following features are planned for future releases:

* Better versioning support (>=, ==, <=, etc.)
* Support for apt versioning
* apt PPA support
* Support for other package managers
* Support for scripted installs from source
* Export to requirements files for various package management systems
