from mock import MagicMock
from depman import Pip, Operation, Ge
from nose.tools import assert_raises
from syn.base_utils import assign, is_hashable
from depman import pip as depd
from depman.pip import Install

#-------------------------------------------------------------------------------
# Pip

def test_pip():
    pip = Pip('six')
    assert pip.order == Pip.order
    assert not pip.always_upgrade
    assert is_hashable(pip)

    assert 'syn' in pip.freeze
    assert 'six' in pip.freeze

    assert pip.check()

    with assign(pip, 'version', Ge('0')):
        assert pip.check()

    with assign(pip, 'version', Ge('100000000000')):
        assert not pip.check()
        
    with assign(pip, 'name', 'foobarbaz123789'):
        assert not pip.check()

    with assign(depd, 'command', MagicMock()):
        pip.satisfy()
        assert depd.command.call_count == 0

        with assign(pip, 'name', 'foobarbaz123789'):
            ops = pip.satisfy()
            assert ops == [Install('foobarbaz123789', order=Pip.order)]
            Operation.optimize(ops)
            for op in ops:
                op.execute()
            depd.command.assert_called_with('pip install --upgrade foobarbaz123789')

        with assign(pip, 'always_upgrade', True):
            ops = pip.satisfy()
            assert ops == [Install('six', order=Pip.order)]
            Operation.optimize(ops)
            for op in ops:
                op.execute()
            depd.command.assert_called_with('pip install --upgrade six')

    def bad_output(*args, **kwargs):
        raise OSError()

    with assign(depd, 'output', bad_output):
        with assign(Pip, 'freeze', dict()):
            Pip._populate_freeze()
            assert Pip.freeze == {}

#-------------------------------------------------------------------------------
