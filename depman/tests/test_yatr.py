from mock import MagicMock
from depman import Yatr, Operation
from depman import yatr as depd
from syn.base_utils import assign, is_hashable

#-------------------------------------------------------------------------------
# Yatr

def test_yatr():
    yatr = Yatr('foo bar')
    assert yatr.name == 'foo bar'
    assert yatr.order == Yatr.order
    assert is_hashable(yatr)

    assert not yatr.check()
    assert not yatr.installed()

    with assign(depd, 'command', MagicMock()):
        ops = yatr.satisfy()
        assert len(ops) == 1

        Operation.optimize(ops)
        for op in ops:
            op.execute()
        assert depd.command.call_count == 1
        depd.command.assert_called_with('yatr foo bar')


    yatr2 = Yatr.from_conf({'bar baz':
                            {'order': -30,
                             'yatrfile': '/foo/bar.yml'}})
    assert yatr2.order == -30

    with assign(depd, 'command', MagicMock()):
        ops = yatr2.satisfy()
        assert len(ops) == 1

        Operation.optimize(ops)
        for op in ops:
            op.execute()
        assert depd.command.call_count == 1
        depd.command.assert_called_with('yatr -f /foo/bar.yml bar baz')


#-------------------------------------------------------------------------------
