from mock import MagicMock
from depman import Pip
from syn.base_utils import assign
from depman import pip as depd

#-------------------------------------------------------------------------------
# Pip

def test_pip():
    pip = Pip('six')
    assert pip.version == ''
    assert pip.order == 3
    assert not pip.always_upgrade
    
    assert 'syn' in pip.freeze
    assert 'six' in pip.freeze

    assert pip.check()

    with assign(pip, 'version', '0'):
        assert pip.check()

    with assign(pip, 'version', '100000000000'):
        assert not pip.check()
        
    with assign(pip, 'name', 'foobarbaz123789'):
        assert not pip.check()

    with assign(depd, 'command', MagicMock()):
        pip.satisfy()
        assert depd.command.call_count == 0

        with assign(pip, 'name', 'foobarbaz123789'):
            pip.satisfy()
            depd.command.assert_called_with('pip install --upgrade foobarbaz123789')

        with assign(pip, 'always_upgrade', True):
            pip.satisfy()
            depd.command.assert_called_with('pip install --upgrade six')

#-------------------------------------------------------------------------------
