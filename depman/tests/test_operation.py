from nose.tools import assert_raises
from depman.operation import subclass_equivalent, Operation, Independent, \
    Combinable, Idempotent, ListView

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

def test_listview():
    lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    lv = ListView(lst, 2, 5)
    assert len(lv) == 3
    assert list(lv) == [2, 3, 4]

    assert lv[0] == 2
    assert lv[1] == 3
    assert lv[2] == 4
    assert lv[-1] == 4
    assert lv[-2] == 3
    assert lv[-3] == 2

    assert_raises(IndexError, lv.__getitem__, 3)
    assert_raises(IndexError, lv.__getitem__, -4)
    assert_raises(IndexError, lv.__setitem__, 3, 8)
    assert_raises(IndexError, lv.__delitem__, 3)

    lv[0] = 10
    assert lst == [0, 1, 10, 3, 4, 5, 6, 7, 8, 9]

    lv.pop(0)
    assert len(lv) == 2
    assert list(lv) == [3, 4]
    assert lst == [0, 1, 3, 4, 5, 6, 7, 8, 9]

    lv.append(10)
    assert list(lv) == [3, 4, 10]
    assert lst == [0, 1, 3, 4, 10, 5, 6, 7, 8, 9]

    lv.pop()
    assert list(lv) == [3, 4]
    assert lst == [0, 1, 3, 4, 5, 6, 7, 8, 9]

    lv.pop()
    lv.pop()
    assert list(lv) == []
    assert lst == [0, 1, 5, 6, 7, 8, 9]

    assert_raises(IndexError, lv.pop)

    lv = ListView(lst, 4, -1)
    assert len(lv) == 3
    assert list(lv) == [7, 8, 9]

    lv.insert(0, 10)
    assert list(lv) == [10, 7, 8, 9]
    assert lst == [0, 1, 5, 6, 10, 7, 8, 9]

    assert_raises(TypeError, ListView, 1, 0, 0)
    assert_raises(ValueError, ListView, [1, 2, 3], 2, 1)
    assert_raises(ValueError, ListView, [1, 2, 3], 5, 7)
    assert_raises(ValueError, ListView, [1, 2, 3], 0, 7)

#-------------------------------------------------------------------------------
# Operation

def test_operation():
    op = Operation('a', 'b', order = 10)

    assert op._list == ['a', 'b']
    assert op.order == 10
    assert op.repetitions == 0

    assert_raises(NotImplementedError, op.execute)
    assert_raises(NotImplementedError, op.combine, op)

#-------------------------------------------------------------------------------
# Operation Reduction

def test_operation_reduction():
    class Op1(Independent): pass
    class Op2(Combinable): pass
    class Op3(Idempotent): pass

    ops = [Op1('a', order=8),
           Op1('b', order=8),
           Op3('c', order=9),
           Op3('d', order=9),
           Op2('e', order=10),
           Op2('f', order=10)]
    
    Operation.optimize(ops)

    assert ops == [Op1('a', order=8),
                   Op1('b', order=8),
                   Op3('c', order=9),
                   Op2('e', 'f', order=10)]

#-------------------------------------------------------------------------------
