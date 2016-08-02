import os
import sys
from shlex import shlex
from syn.five import STR
from mock import MagicMock
from syn.base_utils import assign
from depman.main import main
import depman.dependency as depd
from depman.dependency import Pip

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
    with assign(depd, 'command', MagicMock()):
        with assign(Pip, 'freeze', dict(lxml='', PyYAML='')):
            with assign(depd, 'status', MagicMock(return_value=0)):
                invoke(['satisfy', DEPS1])
                assert depd.command.call_count == 0
                depd.status.assert_any_call('dpkg -s libxml2-dev')
                depd.status.assert_called_with('dpkg -s libxslt1-dev')

#-------------------------------------------------------------------------------
