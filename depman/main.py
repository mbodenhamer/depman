import os
import sys
from syn.type import AnyType
from argparse import ArgumentParser
from .dependency import Dependencies

#-------------------------------------------------------------------------------

DESCRIPTION = 'A lightweight dependency manager.'

parser = ArgumentParser(prog='depman', description=DESCRIPTION)
parser.add_argument('-f', '--depfile', dest='depfile', type=str,
                    default=os.path.join(os.getcwd(), 'requirements.yml'),
                    metavar='<depfile>', help='The requirements file to load')
parser.add_argument('-t', '--type', dest='type', type=str,
                    default='all', metavar='<type>', 
                    help='Restrict operations to dependencies of this type')
parser.add_argument('-o', '--outfile', dest='outfile', type=str, default='',
                    metavar='<outfile>', help='File to write results to')
parser.add_argument('command', metavar='<command>', 
                    choices=['satisfy', 'validate', 'export'],
                    help="'satisfy' satisfies the dependcies specified in "
                    "<depfile>.  'validate' only validates <depfile> and does "
                    "not perform any system operations.  'export' exports "
                    "requirements to a specified file (using -o)")
parser.add_argument('context', metavar='<context>', type=str, default='all',
                    nargs='?',
                    help='The dependency context to perform <command> on')

USAGE = parser.format_usage().strip()

#-------------------------------------------------------------------------------
# Dispatch args

def dispatch_type(typ):
    if typ == 'all':
        return AnyType()

#-------------------------------------------------------------------------------

def _main(*args):
    opts = parser.parse_args(args)
    
    command = opts.command
    context = opts.context
    path = opts.depfile

    optype = dispatch_type(opts.type)

    with open(path, 'rt') as f:
        deps = Dependencies.from_yaml(f)

    if command == 'satisfy':
        deps.satisfy(context, optype)
    elif command == 'validate':
        # We will get an error of some sort before this if it isn't valid
        print("Validation successful")

#-------------------------------------------------------------------------------

def main(): # pragma: no cover
    _main(*sys.argv[1:])

#-------------------------------------------------------------------------------
