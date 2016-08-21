import os
from subprocess import Popen, PIPE
from depman import __version__ as dver

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

    p = Popen('depman version'.format(DEPSEX), 
              stdout=PIPE, shell=True)
    out = p.communicate()[0].decode('utf-8')
    lines = out.strip().split('\n')
    assert lines[-1] == 'depman {}'.format(dver)
    assert p.returncode == 0

#-------------------------------------------------------------------------------
