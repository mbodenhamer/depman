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

    $ pip install depman


Usage
-----
::

    usage: depman [-h] [-f <depfile>] [-t <type>] [-o <outfile>] [--no-header]
		  <command> [<context>]

    A lightweight dependency manager.

    positional arguments:
      <command>             'satisfy' satisfies the dependencies specified in
			    <depfile>. 'validate' only validates <depfile> and
			    does not perform any system operations. 'export'
			    exports requirements to a specified file (using -o)
      <context>             The dependency context to perform <command> on

    optional arguments:
      -h, --help            show this help message and exit
      -f <depfile>, --depfile <depfile>
			    The requirements file to load
      -t <type>, --type <type>
			    Restrict operations to dependencies of this type
      -o <outfile>, --outfile <outfile>
			    File to write results to
      --no-header           No export header

If not supplied, ``<depfile>`` and ``<context>`` default to ``requirements.yml`` and ``all``, respectively.

Example(s)
----------

Suppose you have the following ``requirements.yml`` in your current working directory
::

    includes:
      dev:
	- test

    dev:
      apt:
	- libxml2-dev=2.9.1+dfsg1-5+deb8u2
	- libxslt1-dev
    
      pip:
	- lxml
	- Sphinx

      yatr:
        - install-from-source:
	    before: libxslt1-dev
    
    test:
      pip:
	- nose
	- coverage

    prod:
      pip:
	- gevent:
	    version: '<=1.0.2'
	- syn>=0.0.14
	- six:
	    always_upgrade: yes
	- numpy
	- openopt:
	    after: numpy

      yatr:
	- install-from-source-2:
	    before: gevent
	    after: libxslt1-dev
	- cleanup:
	    yatrfile: other_tasks.yml


This file specifies three dependency contexts: ``dev``, ``test``, ``prod``.  In general, any top-level key in ``requirements.yml`` specifies a dependency context.  The one exception to this rule is ``includes``, which defines inclusion relationships between contexts.  In this example, the ``dev`` context includes the ``test`` context, and so will attempt to satisfy the dependencies for the ``test`` context in addition to the ``dev`` context whenever ``depman satisfy dev`` is run from the command line.
    
Currently, only three dependency types are supported in any context: ``apt``, ``pip``, and ``yatr``.  However, support for other dependency types is planned for future releases (see `Future Features`_).
    
Dependencies are specified in each context under each dependency type as YAML list elements.  If the element is a string, the dependency in question will be treated as satisfied if some version of the package denoted by the string exists on the system.  For more detailed dependency requirements, the name of the package can be listed as the key to a YAML dictionary of dependency options.  This can be seen, for example, in the ``gevent`` dependency, in which a version less than or equal to ``1.0.2`` is specified as a requirement.  Additionally, the ``six`` package contains the ``always_upgrade`` option, which causes depman to always attempt to upgrade the package, regardless of the current version installed.  

Package version relations can be specified in various ways.  In the ``prod`` context, ``pip`` is constrained to only install a version of ``syn`` that is greater than or equal to ``0.0.14``.  Likewise, in the ``dev`` context, ``apt`` is constrained to install version ``2.9.1+dfsg1-5+deb8u2`` of ``libxml2-dev``.  And, as seen above, the ``pip`` ``gevent`` dependency is constrained to a version less than or equal to ``1.0.2``

Relative dependency satisfaction ordering may be specified by use of the ``before`` and ``after`` keys.  In this example, satisfying the ``prod`` context will lead to an invocation of ``pip`` to install ``numpy``, followed by a separate invocation of ``pip`` to install ``openopt``.  Such features are useful for minimizing the hassle of installing of packages that do not properly declare their dependencies.  It should be noted that namespaces are not currently supported, so specifying ``before`` or ``after`` for a name that belongs to multiple dependencies may lead to unexpected results.  The ``before`` and ``after`` keys should only be used when relative ordering is necessary, as unnecessary usage may lead to sub-optimal execution of dependency satisfaction operations.

The ``yatr`` dependency is a special type that will invoke yatr_ to execute the specified task from the specified ``yatrfile`` key.  For example, the ``prod`` context specifies that a task named ``cleanup`` defined in ``other_tasks.yml`` is to be run.  If no ``yatrfile`` key is specified, the specified tasks should be defined in a file named ``yatrfile.yml`` located in the same directory as the depman requirements file.  Unless constrained from doing so by ``before`` and ``after`` specifications, ``depman`` will always attempt to satisfy ``apt`` dependencies before ``pip`` dependencies, and ``pip`` dependencies before running ``yatr`` tasks.  Thus, the ``cleanup`` task will run last in this example if either the ``prod`` or ``all`` contexts are selected.

``yatr`` "dependencies" are not true dependencies, but task invocations, and thus cannot truly be satisfied.  As a result, invoking ``depman`` to satisfy a ``yatr`` dependency will always cause the task defined therein to be executed.  ``yatr`` dependencies can be used to perform scripted installs, cleanup and provisioning actions, and other tasks that are otherwise beyond the scope of a lightweight dependency manager.

On the command line, ``depman`` also accepts the special context ``all`` as a valid parameter.  Running ``depman satisfy all`` causes depman to satisfy the dependencies in all of the defined dependency contexts.  In this example, it would cause depman to satisfy the dependencies for ``dev``, ``test``, and ``prod``.  Running ``depman satisfy`` is equivalent to running ``depman satisfy all``.  

On a machine where none of the specified packages are installed, running ``depman satisfy all`` in this example is equivalent to running the following sequence of commands::

    $ yatr install-from-source
    $ apt-get update
    $ apt-get install -y libxml2-dev=2.9.1+dfsg1-5+deb8u2 libxslt1-dev
    $ yatr install-from-source-2
    $ pip install Sphinx coverage gevent==1.0.2 lxml nose numpy six syn
    $ pip install openopt
    $ yatr -f other_tasks.yml cleanup


Likewise, running ``depman satisfy test`` on a fresh machine is equivalent to::

    $ pip install coverage nose


Running ``depman satisfy dev`` is equivalent to::
 
    $ yatr install-from-source
    $ apt-get update
    $ apt-get install -y libxml2-dev=2.9.1+dfsg1-5+deb8u2 libxslt1-dev
    $ pip install Sphinx coverage lxml nose


And running ``depman satisfy prod`` is equivalent to::

    $ yatr install-from-source-2
    $ pip install gevent==1.0.2 numpy six syn
    $ pip install openopt
    $ yatr -f other_tasks.yml cleanup

.. _yatr: https://github.com/mbodenhamer/yatr

Export
~~~~~~

Dependencies can also be exported.  In this example, running
::

    depman export prod -t pip -o requirements.txt

will produce a file ``requirements.txt`` in the current directory that looks like::

    # Auto-generated by depman 0.3.4
    gevent<=1.0.2
    numpy
    openopt
    six
    syn>=0.0.14

The header comment can be suppressed by supplying the ``--no-header`` option.

.. _Future Features:

Future Features
---------------

The following features are planned for future releases:

* apt PPA support
* Support for other package managers
* Top-level package manager options
* ``any`` context
