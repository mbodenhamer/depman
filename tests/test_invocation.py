from subprocess import Popen, PIPE
from depman.main import USAGE

#-------------------------------------------------------------------------------

def test_invocation():
    p = Popen('depman', stdout=PIPE, shell=True)
    out = p.communicate()[0].decode('utf-8') 
    assert out == USAGE + '\n'
    assert p.returncode == 1

    p = Popen('depman validate all examples/requirements.yml', 
              stdout=PIPE, shell=True)
    out = p.communicate()[0].decode('utf-8')
    lines = out.strip().split('\n')
    assert lines[-1] == 'examples/requirements.yml successfully validated'
    assert p.returncode == 0

#-------------------------------------------------------------------------------
