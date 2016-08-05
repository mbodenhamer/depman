from syn.base import Attr
from .dependency import Dependency, status, command

#-------------------------------------------------------------------------------
# Apt


class Apt(Dependency):
    '''Representation of an apt dependency'''
    key = 'apt'

    _attrs = dict(order = Attr(int, 1))

    def check(self):
        return status('dpkg -s {}'.format(self.name)) == 0

    def satisfy(self):
        if not self.check():
            command('apt-get update')
            command('apt-get install -y {}'.format(self.name))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Apt',)

#-------------------------------------------------------------------------------
