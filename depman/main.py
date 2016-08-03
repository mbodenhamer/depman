import sys
from syn.base_utils import getitem
from .dependency import Dependencies

#-------------------------------------------------------------------------------

USAGE = '''depman <command> [<scope> [<depfile>]]
A lightweight dependency manager.

Possible commands:
    satisfy     Satisfy the dependencies specified in <depfile>
    validate    Validate <depfile> only; do not change the state of the system

Possible scopes:
    all         Combines all possible scopes (default)
    dev         Development dependencies
    prod        Production dependencies

If no values are supplied, <depfile> defaults to "requirements.yml"'''

#-------------------------------------------------------------------------------

def _main(*args):
    if not args:
        print(USAGE)
        sys.exit(1)
        return # for tests when sys.exit() is mocked

    command = args[0]
    scope = getitem(args, 1, 'all')
    path = getitem(args, 2, 'requirements.yml')

    with open(path, 'rt') as f:
        deps = Dependencies.from_yaml(f)

    if command == 'satisfy':
        deps.satisfy(scope)
    elif command == 'validate':
        # We will get an error of some sort before this is it isn't valid
        print("Validation successful")
    else:
        print(USAGE)
        sys.exit(2)

#-------------------------------------------------------------------------------

def main(): # pragma: no cover
    _main(*sys.argv[1:])

#-------------------------------------------------------------------------------
