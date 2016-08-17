from nose.tools import assert_raises
from depman.operation import Operation, Independent, Combinable, Idempotent

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
