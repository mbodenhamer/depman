from subprocess import Popen, PIPE

#-------------------------------------------------------------------------------

def test_invocation():
    p = Popen('depman', stdout=PIPE, shell=True)
    out = p.communicate()[0].decode('utf-8') 
    assert out == 'depman MODE DEPFILE [SCOPE]\n\n'

#-------------------------------------------------------------------------------
