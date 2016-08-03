import os
import sys
from argparse import ArgumentParser
from .dependency import Dependencies

#-------------------------------------------------------------------------------

DESCRIPTION = 'A lightweight dependency manager.'

parser = ArgumentParser(prog='depman', description=DESCRIPTION)
parser.add_argument('-f', '--depfile', dest='depfile', type=str,
                    default=os.path.join(os.getcwd(), 'requirements.yml'),
                    metavar='<depfile>', help='The requirements file to load')
parser.add_argument('command', metavar='<command>', 
                    choices=['satisfy', 'validate'],
                    help="'satisfy' satisfies the dependcies specified in "
                    "<depfile>.  'validate' only validates <depfile> and does "
                    "not perform any system operations")
parser.add_argument('context', metavar='<context>', type=str, default='all',
                    nargs='?',
                    help='The dependency context to perform <command> on')

USAGE = parser.format_usage().strip()

#-------------------------------------------------------------------------------

def _main(*args):
    opts = parser.parse_args(args)
    
    command = opts.command
    context = opts.context
    path = opts.depfile

    with open(path, 'rt') as f:
        deps = Dependencies.from_yaml(f)

    if command == 'satisfy':
        deps.satisfy(context)
    elif command == 'validate':
        # We will get an error of some sort before this if it isn't valid
        print("Validation successful")

#-------------------------------------------------------------------------------

def main(): # pragma: no cover
    _main(*sys.argv[1:])

#-------------------------------------------------------------------------------
