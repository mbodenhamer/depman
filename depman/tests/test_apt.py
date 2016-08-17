from mock import MagicMock
from depman import Apt, Operation
from syn.base_utils import assign, is_hashable
from depman import apt as depd
from depman.apt import Install, Update

#-------------------------------------------------------------------------------
# Apt

def test_apt():
    apt = Apt('make')
    assert apt.name == 'make'
    assert apt.order == Apt.order
    assert is_hashable(apt)

    with assign(depd, 'command', MagicMock()):
        with assign(depd, 'status', MagicMock(return_value=0)):
            assert apt.check()
            depd.status.assert_called_once_with('dpkg -s make')

            assert apt.satisfy() == []
            assert depd.command.call_count == 0

        with assign(depd, 'status', MagicMock(return_value=1)):
            assert not apt.check()
            depd.status.assert_called_once_with('dpkg -s make')

            ops = apt.satisfy()
            assert ops == [Update(order=Apt.order),
                           Install('make', order=Apt.order)]

            # Make sure update precedes install
            assert ops[0].order == Apt.order - 1
            assert ops[1].order == Apt.order

            Operation.optimize(ops)
            for op in ops:
                op.execute()
            assert depd.command.call_count == 2
            depd.command.assert_any_call('apt-get update')
            depd.command.assert_called_with('apt-get install -y make')

#-------------------------------------------------------------------------------
