from syn.base import Attr
from .dependency import Dependency, status, command
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
    order = 10

    _attrs = dict(order = Attr(int, order))

    def check(self):
        return status('dpkg -s {}'.format(self.name)) == 0

    def satisfy(self):
        if not self.check():
            return [Update(order=self.order),
                    Install(self.name, order=self.order)]
        return []


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Apt',)

#-------------------------------------------------------------------------------
