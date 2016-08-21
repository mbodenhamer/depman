import os
from syn.base import Attr
from mock import MagicMock
from nose.tools import assert_raises
from depman import dependency as depd
from syn.base_utils import assert_equivalent, assign, is_hashable
from depman import Dependency, Dependencies, Apt, Pip, Eq
from depman import apt as aptd
from depman import pip as pipd
from depman.main import dispatch_type
from depman import __version__ as dver

#-------------------------------------------------------------------------------

DIR = os.path.dirname(os.path.abspath(__file__))
DEPS1 = os.path.join(DIR, '../../tests/deps1.yml')
DEPS2 = os.path.join(DIR, '../../tests/deps2.yml')
DEPS3 = os.path.join(DIR, '../../tests/deps3.yml')
DEPS4 = os.path.join(DIR, '../../tests/deps4.yml')
DEPS5 = os.path.join(DIR, '../../tests/deps5.yml')
DEPS6 = os.path.join(DIR, '../../tests/deps6.yml')
TEST1 = os.path.join(DIR, 'test1')

#-------------------------------------------------------------------------------
# Utilities

def test_command():
    out, code = depd.command('true')
    assert out == ''
    assert code == 0

    depd.command('true', silent=False)

def test_output():
    assert depd.output('pwd').strip() == os.path.abspath(os.getcwd())

def test_status():
    assert depd.status('true') == 0
    assert depd.status('false') == 1

#-------------------------------------------------------------------------------
# Dependency

def test_dependency():
    assert depd.DEPENDENCY_KEYS == dict(apt = Apt,
                                        pip = Pip)
    assert depd.DEPENDENCY_ORDERS == dict(apt = Apt.order,
                                          pip = Pip.order)
    

    dep = Dependency('foo')
    assert dep.name == 'foo'
    assert not dep.installed()
    assert not dep.check()
    assert_raises(NotImplementedError, dep.satisfy)

    assert_equivalent(Dependency.from_conf('foo'), dep)
    assert_raises(TypeError, Dependency.from_conf, [])
    assert_raises(TypeError, Dependency.from_conf, dict(a = 1, b = 2))

    class Foo(Dependency):
        _attrs = dict(a = Attr(int),
                      b = Attr(int))
        
    assert_equivalent(Foo.from_conf(dict(foo = dict(a = 1, b = 2))),
                      Foo('foo', a = 1, b = 2))

    f = Foo('bar', a = 1, b = 2, order=5)
    assert is_hashable(f)

#-------------------------------------------------------------------------------
# Dependencies

def test_dependencies():
    def assert_listeq(A, B):
        for a in A:
            assert a in B
        for b in B:
            assert b in A

    with open(DEPS1, 'rt') as f:
        deps = Dependencies.from_yaml(f)
        
    contexts = dict(dev = [Apt('libxml2-dev'),
                           Apt('libxslt1-dev'),
                           Pip('lxml')],
                    prod = [Pip('PyYAML')])
    assert_equivalent(deps, Dependencies(contexts=contexts))

    assert_listeq(deps.deps_from_context('all'),
                  deps.contexts.dev + deps.contexts.prod)

    assert deps.deps_from_context('dev') == deps.contexts.dev
    assert deps.deps_from_context('prod') == deps.contexts.prod
    assert_raises(ValueError, deps.deps_from_context, 'foo')

    with open(DEPS2, 'rt') as f:
        deps2 = Dependencies.from_yaml(f)

    contexts = dict(dev = [Apt('gcc', order=0),
                           Apt('make')])

    assert_equivalent(deps2, Dependencies(contexts = contexts))
    assert deps2.deps_from_context('all') == deps2.contexts.dev
    assert deps2.deps_from_context('dev') == deps2.contexts.dev
    assert_raises(ValueError, deps2.deps_from_context, 'prod')

    with open(DEPS3, 'rt') as f:
        deps3 = Dependencies.from_yaml(f)

    contexts = dict(prod = [Pip('six'),
                            Pip('syn', version=Eq('0.0.7'),
                                always_upgrade=True)])

    assert_equivalent(deps3, Dependencies(contexts=contexts))
    assert deps3.deps_from_context('all') == deps3.contexts.prod
    assert_raises(ValueError, deps3.deps_from_context, 'dev')
    assert deps3.deps_from_context('prod') == deps3.contexts.prod

    with open(DEPS4, 'rt') as f:
        deps4 = Dependencies.from_yaml(f)

    assert 'includes' not in deps4.contexts

    assert_listeq(deps4.deps_from_context('c1'),
                  deps4.contexts.c1 + deps4.contexts.c2 +
                  deps4.contexts.c3 + deps4.contexts.c4)

    assert_listeq(deps4.deps_from_context('c2'),
                  deps4.contexts.c2 + deps4.contexts.c3)

    assert_listeq(deps4.deps_from_context('c3'), deps4.contexts.c3)
    assert_listeq(deps4.deps_from_context('c4'), deps4.contexts.c4)
    assert_listeq(deps4.deps_from_context('c5'), deps4.contexts.c5)

    assert_raises(AssertionError, Dependencies,
                  contexts = dict(c1 = [Apt('make')],
                                  c2 = [Pip('six')]),
                  includes = dict(c1 = ['c2', 'c3']))
    
    assert_raises(AssertionError, Dependencies,
                  contexts = dict(c1 = [Apt('make')],
                                  c2 = [Pip('six')]),
                  includes = dict(c3 = ['c2', 'c2']))

    with open(DEPS5, 'rt') as f:
        deps5 = Dependencies.from_yaml(f)
   
    with assign(Apt, '_pkgs', dict()):
        with assign(Pip, '_pkgs', dict()):
            from depman.apt import Install, Update
            from depman.pip import Install as PipInstall

            ops = deps5.satisfy('prod', execute=False)
            assert ops == [Update(order=Apt.order),
                           Install('a', 'b', 'c', 'd', order=Apt.order),
                           PipInstall('a', 'b', 'c', order=Pip.order)]
            
            with assign(aptd, 'command', MagicMock()):
                with assign(pipd, 'command', MagicMock()):
                    deps5.satisfy('prod')

                    assert aptd.command.call_count == 2
                    aptd.command.assert_any_call('apt-get update')
                    aptd.command.assert_any_call('apt-get install -y a b c d')

                    assert pipd.command.call_count == 1
                    pipd.command.assert_any_call('pip install --upgrade a b c')

    with open(DEPS6, 'rt') as f:
        deps6 = Dependencies.from_yaml(f)
        
    hdr = deps6.export_header()
    assert hdr == '# Auto-generated by depman {}\n'.format(dver)
    
    out = deps6.export('all', dispatch_type('pip'), None, write=False)
    eout = hdr + 'a\nb==1.2\nc<=1.2\nd>=1.2' # expected output (or export output)
    assert out == eout

    with open(TEST1, 'wt') as f:
        deps6.export('prod', dispatch_type('pip'), f)
    with open(TEST1, 'rt') as f:
        assert f.read() == eout

    with assign(Apt, '_pkgs', dict(a='1', b='1.3', c='1.3', f='1')):
        with assign(Pip, '_pkgs', dict(a='1', b='1.3', c='1.3')):
            from depman.apt import Install, Update, Remove
            from depman.pip import Install as PipInstall
            
            ops = deps6.satisfy('prod', execute=False)
            assert ops == [Remove('b', 'c', order=Apt.order),
                           Update(order=Apt.order),
                           Install('b=1.2', 'c=1.2', 'd', 'e=1.3', 'f',
                                   order=Apt.order),
                           PipInstall('b==1.2', 'c==1.2', 'd', order=Pip.order)]

            with assign(aptd, 'command', MagicMock()):
                with assign(pipd, 'command', MagicMock()):
                    deps6.satisfy('prod')
                    
                    assert aptd.command.call_count == 3
                    aptd.command.assert_any_call('apt-get remove -y b c')
                    aptd.command.assert_any_call('apt-get update')
                    aptd.command.assert_any_call('apt-get install -y b=1.2 '
                                                 'c=1.2 d e=1.3 f')

                    assert pipd.command.call_count == 1
                    pipd.command.assert_any_call('pip install --upgrade b==1.2 '
                                                 'c==1.2 d')

#-------------------------------------------------------------------------------
