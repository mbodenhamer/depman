import os
from shlex import shlex
from mock import MagicMock
from syn.base_utils import assign
from depman.main import main
import depman.main as depm

#-------------------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))
APP1 = os.path.join(DIR, 'app1')

#-------------------------------------------------------------------------------

def test_main_1():
    def invoke(cmd):
        main(*shlex(cmd))

    with assign(depm, 'exit', MagicMock()):
        invoke('')
        depm.exit.assert_called_once_with(1)

#-------------------------------------------------------------------------------
