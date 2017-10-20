import os
from mock import MagicMock
from depman import Dependencies, Operation
from syn.base_utils import assign
from depman import yatr as _yatr
from depman import pip as _pip
from depman import apt as _apt

DIR = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------------------------------------------------
# Test 1

def test1():
    with open(os.path.join(DIR, 'test1.yml'), 'r') as f:
        deps = Dependencies.from_yaml(f)

    ops = []
    for dep in deps.deps_from_context('all'):
        ops.extend(dep.satisfy())

    Operation.optimize(ops)
    assert len(ops) == 6

    with assign(_yatr, 'command', MagicMock()):
        ops[0].execute()
        assert _yatr.command.call_count == 1
        _yatr.command.assert_called_with('yatr -f /foo/bar.yml init')

    with assign(_apt, 'command', MagicMock()):
        ops[1].execute()
        assert _apt.command.call_count == 1
        _apt.command.assert_called_with('apt-get update')

    with assign(_apt, 'command', MagicMock()):
        ops[2].execute()
        assert _apt.command.call_count == 1
        _apt.command.assert_called_with('apt-get install -y foo123')

    with assign(_pip, 'command', MagicMock()):
        ops[3].execute()
        assert _pip.command.call_count == 1
        _pip.command.assert_called_with('pip install --upgrade bar456')

    with assign(_pip, 'command', MagicMock()):
        ops[4].execute()
        assert _pip.command.call_count == 1
        _pip.command.assert_called_with('pip install --upgrade openopt')

    with assign(_yatr, 'command', MagicMock()):
        ops[5].execute()
        assert _yatr.command.call_count == 1
        _yatr.command.assert_called_with('yatr -f /foo/bar.yml cleanup')

#-------------------------------------------------------------------------------
