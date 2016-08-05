from syn.five import STR
from syn.base import init_hook, Attr
from .dependency import Dependency, command, output
from .operation import Combinable

#-------------------------------------------------------------------------------
# Pip Operations

#-----------------------------------------------------------
# pip install


class Install(Combinable):
    def execute(self):
        args = ' '.join(map(str, self))
        command('pip install --upgrade {}'.format(args))


#-------------------------------------------------------------------------------
# Pip


class Pip(Dependency):
    '''Representation of a pip dependency'''
    key = 'pip'
    freeze = dict()
    order = 30

    _attrs = dict(version = Attr(STR, default='',
                                 doc='Minimum version required'),
                  always_upgrade = Attr(bool, default=False,
                                        doc='Always attempt to upgrade'),
                  order = Attr(int, order))

    @init_hook
    def _populate_freeze(self):
        cls = type(self)
        if not cls.freeze:
            pkgs = output('pip freeze')
            cls.freeze = dict([tuple(line.split('==')) 
                               for line in pkgs.split('\n') if line])

    def check(self):
        if self.name in self.freeze:
            if self.version: 
                if self.version <= self.freeze[self.name]:
                    return True
                else:
                    return False
            else:
                return True
        return False

    def satisfy(self):
        if not self.check() or self.always_upgrade:
            return [Install(self.name, order=self.order)]
        return []


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Pip',)

#-------------------------------------------------------------------------------
