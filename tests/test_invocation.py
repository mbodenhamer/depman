import os
from subprocess import Popen, PIPE
from depman.main import USAGE

#-------------------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))
DEPSEX = os.path.join(DIR, 'examples/requirements.yml')

#-------------------------------------------------------------------------------

def test_invocation():
    p = Popen('depman validate -f {}'.format(DEPSEX), 
              stdout=PIPE, shell=True)
    out = p.communicate()[0].decode('utf-8')
    lines = out.strip().split('\n')
    assert lines[-1] == 'Validation successful'
    assert p.returncode == 0

#-------------------------------------------------------------------------------
