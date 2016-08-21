from fnmatch import fnmatch
from syn.base import Attr, create_hook
from .dependency import Dependency, command, output
from .operation import Idempotent, Combinable
from .relation import Eq, Le

#-------------------------------------------------------------------------------
# Apt Operations

#------------------------------------------------------------
# apt-get install


class Install(Combinable):
    def execute(self):
        args = ' '.join(map(str, self))
        command('apt-get install -y {}'.format(args))


#------------------------------------------------------------
# apt-get remove


class Remove(Combinable):
    order_offset = -3
    def execute(self):
        args = ' '.join(map(str, self))
        command('apt-get remove -y {}'.format(args))


#------------------------------------------------------------
# apt-get update


class Update(Idempotent):
    order_offset = -1

    def execute(self):
        command('apt-get update')


#-------------------------------------------------------------------------------
# Apt

class Apt(Dependency):
    '''Representation of an apt dependency'''
    key = 'apt'
    order = 10

    _attrs = dict(order = Attr(int, order))

    @classmethod
    @create_hook
    def _populate_pkgs(cls):
        if not cls._pkgs:
            try:
                lines = output('dpkg -l').split('\n')
                partss = [l.split() for l in lines[5:] if l]
                pkgs = [(p[1], p[2]) for p in partss if fnmatch(p[0], '?i')]
                cls._pkgs = dict(pkgs)
            except OSError:
                pass

    def satisfy(self):
        up = [Update(order=self.order)]
        inst = up + [Install(self.name, order=self.order)]
        instver = up + [Install('{}={}'.format(self.name, self.version.rhs),
                                order=self.order)]
        down = [Remove(self.name, order=self.order)] + instver

        if self.always_upgrade:
            return inst
        
        if not self.check():
            if isinstance(self.version, (Eq, Le)):
                if self.installed():
                    return down
                return instver
            return inst
        return []


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Apt',)

#-------------------------------------------------------------------------------
