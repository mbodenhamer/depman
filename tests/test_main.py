import os
from shlex import shlex
from syn.five import STR
from mock import MagicMock
from syn.base_utils import assign
from depman.main import _main
import depman.apt as aptd
import depman.pip as pipd
from depman import Pip, Apt

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
    with assign(aptd, 'command', MagicMock()):
        with assign(pipd, 'command', MagicMock()):
            with assign(Pip, 'freeze', dict(lxml='', PyYAML='')):
                with assign(Apt, 'pkgs', {'libxml2-dev': '',
                                          'libxslt1-dev': ''}):
                    invoke(['satisfy', '-f', DEPS1])
                    assert aptd.command.call_count == 0
                    assert pipd.command.call_count == 0

    # Validate
    with assign(aptd, 'command', MagicMock()):
        with assign(pipd, 'command', MagicMock()):
            with assign(Pip, 'freeze', dict(lxml='', PyYAML='')):
                invoke(['validate', '-f', DEPS1])
                assert aptd.command.call_count == 0
                assert pipd.command.call_count == 0

    # Validate the example file(s)
    invoke(['validate', '-f', DEPSEX])

#-------------------------------------------------------------------------------
