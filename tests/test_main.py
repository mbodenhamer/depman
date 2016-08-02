import os
import sys
from shlex import shlex
from syn.five import STR
from mock import MagicMock
from syn.base_utils import assign
from depman.main import main

#-------------------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))
DEPS1 = os.path.join(DIR, 'deps1.yml')

#-------------------------------------------------------------------------------

def test_main():
    def invoke(cmd):
        if  isinstance(cmd, STR):
            main(*shlex(cmd))
        else:
            main(*cmd)

    # No args
    with assign(sys, 'exit', MagicMock()):
        invoke('')
        sys.exit.assert_called_once_with(1)

    # Bad mode
    with assign(sys, 'exit', MagicMock()):
        invoke(['foo', DEPS1])
        sys.exit.assert_called_once_with(2)

    # Satisfy

    # Check

#-------------------------------------------------------------------------------
