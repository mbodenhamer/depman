from mock import MagicMock
from depman import Apt
from syn.base_utils import assign
from depman import apt as depd

#-------------------------------------------------------------------------------
# Apt

def test_apt():
    apt = Apt('make')
    assert apt.name == 'make'
    assert apt.order == 1

    with assign(depd, 'command', MagicMock()):
        with assign(depd, 'status', MagicMock(return_value=0)):
            assert apt.check()
            depd.status.assert_called_once_with('dpkg -s make')

            apt.satisfy()
            assert depd.command.call_count == 0

        with assign(depd, 'status', MagicMock(return_value=1)):
            assert not apt.check()
            depd.status.assert_called_once_with('dpkg -s make')

            apt.satisfy()
            assert depd.command.call_count == 2
            depd.command.assert_any_call('apt-get update')
            depd.command.assert_called_with('apt-get install -y make')

#-------------------------------------------------------------------------------
