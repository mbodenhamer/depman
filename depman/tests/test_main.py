from nose.tools import assert_raises
from syn.type import AnyType, TypeType, MultiType
from depman import Apt, Pip

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
