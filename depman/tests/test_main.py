import os
import sys
from nose.tools import assert_raises
from syn.type import AnyType, TypeType, MultiType
from depman import Apt, Pip

#-------------------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))
TEST1 = os.path.join(DIR, 'test1')

#-------------------------------------------------------------------------------
# Dispatch type

def test_dispatch_type():
    from depman.main import dispatch_type

    assert dispatch_type('all') == AnyType()
    assert dispatch_type('apt') == TypeType(Apt)
    assert dispatch_type('pip') == TypeType(Pip)
    assert dispatch_type('apt,pip') == MultiType([TypeType(Apt), TypeType(Pip)])
    assert_raises(TypeError, dispatch_type, 'foo')

#-------------------------------------------------------------------------------
# Dispatch outfile

def test_dispatch_outfile():
    from depman.main import dispatch_outfile

    assert dispatch_outfile('') is sys.stdout
    
    f = dispatch_outfile(TEST1)
    assert f.name == TEST1
    f.close()

#-------------------------------------------------------------------------------
