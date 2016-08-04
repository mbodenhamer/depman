from copy import deepcopy
from nose.tools import assert_raises
from depman.operation import subclass_equivalent, Operation

#-------------------------------------------------------------------------------
# Utilities

def test_subclass_equivalent():
    class A(object): pass
    class B(object): pass
    class A1(A): pass
    class A2(A): pass
    class A11(A1): pass

    assert not subclass_equivalent(A, B)
    assert not subclass_equivalent(A(), B())
    assert_raises(TypeError, subclass_equivalent, A, B())
    assert_raises(TypeError, subclass_equivalent, A(), B)

    assert subclass_equivalent(A, A)
    assert subclass_equivalent(A, A1)
    assert subclass_equivalent(A1, A11)

    assert not subclass_equivalent(A11, A2)

#-------------------------------------------------------------------------------
# Operation

def test_operation():
    op = Operation('a', 'b', order = 10)

    assert op._list == ['a', 'b']
    assert op.order == 10
    assert op.repetitions == 0

    assert_raises(NotImplementedError, op.execute)

    op2 = Operation('c', order = 10)
    op3 = Operation('d', order = 10)
    
    ops = [op2, op3]
    cops = deepcopy(ops)
    assert op.combine(op2) is None

    op.reduce(ops)
    assert ops == cops

#-------------------------------------------------------------------------------
