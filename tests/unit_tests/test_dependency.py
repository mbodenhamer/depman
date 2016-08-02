import os
from syn.base import Attr
from mock import MagicMock
from nose.tools import assert_raises
from depman import dependency as depd
from syn.base_utils import assign, assert_equivalent
from depman.dependency import Dependency, Dependencies, Pip, Apt

#-------------------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))
DEPS1 = os.path.join(DIR, '../deps1.yml')

#-------------------------------------------------------------------------------
# Utilities

def test_command():
    assert depd.command('pwd').strip() == os.path.abspath(os.getcwd())

def test_status():
    assert depd.status('true') == 0
    assert depd.status('false') == 1

#-------------------------------------------------------------------------------
# Dependency

def test_dependency():
    assert depd.DEPENDENCY_KEYS == dict(apt = Apt,
                                        pip = Pip)

    dep = Dependency('foo')
    assert dep.name == 'foo'
    assert_raises(NotImplementedError, dep.check)
    assert_raises(NotImplementedError, dep.satisfy)

    assert_equivalent(Dependency.from_conf('foo'), dep)
    assert_raises(TypeError, Dependency.from_conf, [])
    assert_raises(TypeError, Dependency.from_conf, dict(a = 1, b = 2))

    class Foo(Dependency):
        _attrs = dict(a = Attr(int),
                      b = Attr(int))

    assert_equivalent(Foo.from_conf(dict(foo = dict(a = 1, b = 2))),
                      Foo('foo', a = 1, b = 2))

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
# Dependencies

def test_dependencies():
    with open(DEPS1, 'rt') as f:
        deps = Dependencies.from_yaml(f)

    assert_equivalent(deps, Dependencies(dev = [Apt('libxml2-dev'),
                                                Apt('libxslt1-dev'),
                                                Pip('lxml')],
                                         prod = [Pip('PyYAML')]))

    assert deps.deps_from_scope('all') == deps.dev + deps.prod
    assert deps.deps_from_scope('dev') == deps.dev
    assert deps.deps_from_scope('prod') == deps.prod
    assert_raises(ValueError, deps.deps_from_scope, 'foo')

#-------------------------------------------------------------------------------
