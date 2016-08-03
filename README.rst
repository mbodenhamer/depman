depman
======

.. image:: https://travis-ci.org/mbodenhamer/depman.svg?branch=master
    :target: https://travis-ci.org/mbodenhamer/depman
    
.. image:: https://img.shields.io/coveralls/mbodenhamer/depman.svg
    :target: https://coveralls.io/r/mbodenhamer/depman

.. image:: https://readthedocs.org/projects/depman/badge/?version=latest
    :target: http://depman.readthedocs.org/en/latest/?badge=latest

A lightweight dependency manager.

Installation
------------
::

    $ pip install -U depman


Usage
-----
::

    depman <command> [<scope> [<depfile>]]
    A lightweight dependency manager.

    Possible commands:
	satisfy     Satisfy the dependencies specified in <depfile>

    Possible scopes:
	all         Combines all possible scopes (default)
	dev         Development dependencies
	prod        Production dependencies

    If no values are supplied, <depfile> defaults to "requirements.yml"

Example(s)
----------

Suppose you have the following `requirements.yml` in your current working directory::

    dev:
      apt:
	- libxml2-dev
	- libxslt1-dev
      pip:
	- lxml

    prod:
      pip:
	- gevent:
	    version: 1.0.2
	- texttable
	- syn:
	    always_upgrade: yes

Running `depman satisfy dev` will install the development dependencies specified in `requirements.yml`.  First, it will use `apt-get` to install `libxml2-dev` and `libxslt1-dev` (both dependencies for `lxml`) and then use `pip` to install `lxml`.  In general, all `apt` dependencies are satisfied before `pip` dependencies.
    
Running `depman satisfy prod` will install the production dependencies specified in `requirements.yml`.  As there are only `pip` dependencies, it will use `pip` to install `gevent` (if either `gevent` is not currently installed, or if installed, has a version lower than 1.0.2), `texttable` (if `texttable`, regardless of version, is not currently installed), and `syn`.  Because the `always_upgrade` option is set, pip will always attempt to upgrade `syn` when `depman satisfy` is run.

Running `depman satisfy` will satisfy both the development and production dependencies specified in `requirements.yml`.

Future Features
---------------

The following features are planned for future releases:

* Better versioning support (>=, ==, <=, etc.)
* Support for apt versioning
* apt PPA support
* Better command-line argument parsing / usage information
* YAML file validation
* Dependency satisfaction optimizations
* yum support
* Support for scripted installs from source
* Support for user-definable scopes
