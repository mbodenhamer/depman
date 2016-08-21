import os
import sys
from syn.type import Type, AnyType
from argparse import ArgumentParser
from .dependency import Dependencies, DEPENDENCY_KEYS
from . import __version__ as dver

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
parser.add_argument('--no-header', dest='no_header', default=False, 
                    action='store_true', help='No export header')
parser.add_argument('command', metavar='<command>', 
                    choices=['satisfy', 'validate', 'export', 'version'],
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

def dispatch_type(typ):
    if typ == 'all':
        return AnyType()
    if ',' in typ:
        return Type.dispatch(tuple([dispatch_type(t) for t in typ.split(',')]))
    if typ in DEPENDENCY_KEYS:
        return Type.dispatch(DEPENDENCY_KEYS[typ])
    raise TypeError("Unknown type: {}".format(typ))

#-------------------------------------------------------------------------------
# Dispatch outfile

def dispatch_outfile(f):
    if not f:
        return sys.stdout
    return open(f, 'wt')

#-------------------------------------------------------------------------------

def _main(*args):
    opts = parser.parse_args(args)
    
    command = opts.command
    context = opts.context
    path = opts.depfile
    include_header = not opts.no_header

    if command == 'version':
        print('depman {}'.format(dver))
        return

    deptype = dispatch_type(opts.type)

    with open(path, 'rt') as f:
        deps = Dependencies.from_yaml(f)

    outfile = dispatch_outfile(opts.outfile)
    if command == 'satisfy':
        deps.satisfy(context, deptype)
    elif command == 'validate':
        # We will get an error of some sort before this if it isn't valid
        print("Validation successful")
    elif command == 'export':
        deps.export(context, deptype, outfile, include_header=include_header)

    if outfile is not sys.stdout:
        outfile.close()

#-------------------------------------------------------------------------------

def main():
    _main(*sys.argv[1:]) # pragma: no cover

#-------------------------------------------------------------------------------
