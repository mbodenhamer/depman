import os
from shlex import shlex
from syn.five import STR
from mock import MagicMock
from syn.base_utils import assign
from depman.main import _main
import depman.dependency as depd
from depman.dependency import Pip

#-------------------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))
DEPS1 = os.path.join(DIR, 'deps1.yml')
DEPSEX = os.path.join(DIR, 'examples/requirements.yml')

#-------------------------------------------------------------------------------

def test_main():
    def invoke(cmd):
        if  isinstance(cmd, STR):
            _main(*shlex(cmd))
        else:
            _main(*cmd)

    # Satisfy
    with assign(depd, 'command', MagicMock()):
        with assign(Pip, 'freeze', dict(lxml='', PyYAML='')):
            with assign(depd, 'status', MagicMock(return_value=0)):
                invoke(['satisfy', '-f', DEPS1])
                assert depd.command.call_count == 0
                depd.status.assert_any_call('dpkg -s libxml2-dev')
                depd.status.assert_called_with('dpkg -s libxslt1-dev')

    # Validate
    with assign(depd, 'command', MagicMock()):
        with assign(Pip, 'freeze', dict(lxml='', PyYAML='')):
            invoke(['validate', '-f', DEPS1])
            assert depd.command.call_count == 0

    # Validate the example file(s)
    invoke(['validate', '-f', DEPSEX])

#-------------------------------------------------------------------------------
