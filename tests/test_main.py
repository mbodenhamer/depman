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
DEPS6 = os.path.join(DIR, 'deps6.yml')
DEPSEX = os.path.join(DIR, 'examples/requirements.yml')
TEST1 = os.path.join(DIR, 'test1')

#-------------------------------------------------------------------------------

def test_main():
    def invoke(cmd):
        if  isinstance(cmd, STR):
            _main(*shlex.split(cmd))
        else:
            _main(*cmd)

    # Satisfy
    with assign(aptd, 'command', MagicMock()):
        with assign(pipd, 'command', MagicMock()):
            with assign(Pip, '_pkgs', dict(lxml='', PyYAML='')):
                with assign(Apt, '_pkgs', {'libxml2-dev': '',
                                          'libxslt1-dev': ''}):
                    invoke(['satisfy', '-f', DEPS1])
                    assert aptd.command.call_count == 0
                    assert pipd.command.call_count == 0

    # Validate
    with assign(aptd, 'command', MagicMock()):
        with assign(pipd, 'command', MagicMock()):
            with assign(Pip, '_pkgs', dict(lxml='', PyYAML='')):
                invoke(['validate', '-f', DEPS1])
                assert aptd.command.call_count == 0
                assert pipd.command.call_count == 0

    # Validate the example file(s)
    invoke(['validate', '-f', DEPSEX])

    # Export
    eout = 'a\nb==1.2\nc<=1.2\nd>=1.2'
    invoke(['export', '-f', DEPS6, '-t', 'pip', '-o', TEST1, '--no-header'])
    with open(TEST1, 'rt') as f:
        assert f.read() == eout

    #Version
    invoke(['version', '-f', DEPS6])

#-------------------------------------------------------------------------------
