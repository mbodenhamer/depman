from fnmatch import fnmatch
from syn.base import Attr, init_hook
from .dependency import Dependency, status, command, output
from .operation import Idempotent, Combinable

#-------------------------------------------------------------------------------
# Apt Operations

#------------------------------------------------------------
# apt-get install


class Install(Combinable):
    def execute(self):
        args = ' '.join(map(str, self))
        command('apt-get install -y {}'.format(args))


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
    pkgs = dict()
    order = 10

    _attrs = dict(order = Attr(int, order))

    @init_hook
    def _populate_pkgs(self):
        cls = type(self)
        if not cls.pkgs:
            lines = output('dpkg -l').split('\n')
            partss = [l.split() for l in lines[5:] if l]
            pkgs = [(p[1], p[2]) for p in partss if fnmatch(p[0], '?!')]
            cls.pkgs = dict(pkgs)

    def check(self):
        if self.name in self.pkgs:
            if self.version(self.pkgs[self.name]):
                return True
        return False

    def satisfy(self):
        if not self.check():
            return [Update(order=self.order),
                    Install(self.name, order=self.order)]
        return []


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Apt',)

#-------------------------------------------------------------------------------
