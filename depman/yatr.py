from syn.base import Attr
from syn.five import STR
from .dependency import Dependency, command
from .operation import Independent

#-------------------------------------------------------------------------------
# Yatr Task


class Task(Independent):
    def execute(self):
        args = ' '.join(map(str, self))
        command('yatr {}'.format(args))


#-------------------------------------------------------------------------------
# Yatr


class Yatr(Dependency):
    key = 'yatr'
    order = 99999

    _attrs = dict(order = Attr(int, order),
                  yatrfile = Attr(STR, ''))

    def check(self):
        '''Tasks will always run.'''
        return False

    def installed(self):
        return False

    def satisfy(self):
        args = [self.name] # self.name is the task name + args (optional)
        if self.yatrfile:
            args.insert(0, '-f {}'.format(self.yatrfile))

        task = Task(*args, order=self.order)
        return [task]


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Yatr',)

#-------------------------------------------------------------------------------
