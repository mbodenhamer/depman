import os
import sys
from syn.type import Type, AnyType
from argparse import ArgumentParser
from .dependency import Dependencies
from .apt import Apt
from .pip import Pip

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
# Dispatch type

TYPES = dict(apt = Apt,
             pip = Pip)

def dispatch_type(typ):
    if typ == 'all':
        return AnyType()
    if ',' in typ:
        return Type.dispatch(tuple([dispatch_type(t) for t in typ.split(',')]))
    if typ in TYPES:
        return Type.dispatch(TYPES[typ])
    raise TypeError("Unknown type: {}".format(typ))

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
