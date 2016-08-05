from syn.five import xrange
from operator import attrgetter
from collections import MutableSequence
from syn.base import ListWrapper, Attr, init_hook

#-------------------------------------------------------------------------------
# Utilities

def subclass_equivalent(o1, o2):
    def comp(x, y):
        return issubclass(x, y) or issubclass(y, x)

    if isinstance(o1, type) and isinstance(o2, type):
        return comp(o1, o2)
    elif (isinstance(o1, object) and isinstance(o2, object) and
          not (isinstance(o1, type) or isinstance(o2, type))):
        return comp(type(o1), type(o2))
    raise TypeError("Cannot compare type and object")


class ListView(MutableSequence):
    '''A list view.'''
    def __init__(self, lst, start, end):
        if not isinstance(lst, list):
            raise TypeError("Parameter lst must be type list")

        self.list = lst
        self.start = start
        self.end = end
        if self.end < 0:
            self.end = len(self.list) + self.end + 1

        if self.end < self.start:
            raise ValueError('End less than start')

        if not 0 <= self.start < len(self.list):
            raise ValueError('Invalid start position')

        if not 0 <= self.end <= len(self.list):
            raise ValueError('Invalid end position')

    def _correct_idx(self, idx):
        if idx < 0:
            return self.end + idx
        return self.start + idx

    def __getitem__(self, idx):
        idx = self._correct_idx(idx)
        if not self.start <= idx < self.end:
            raise IndexError("index out of range")
        return self.list[idx]

    def __setitem__(self, idx, value):
        idx = self._correct_idx(idx)
        if not self.start <= idx < self.end:
            raise IndexError("index out of range")
        self.list[idx] = value

    def __delitem__(self, idx):
        idx = self._correct_idx(idx)
        if not self.start <= idx < self.end:
            raise IndexError("index out of range")
        self.list.pop(idx)
        self.end -= 1

    def __iter__(self):
        for k in xrange(self.start, self.end):
            yield self.list[k]

    def __len__(self):
        return self.end - self.start

    def insert(self, idx, obj):
        idx = self._correct_idx(idx)
        self.list.insert(idx, obj)
        self.end += 1


#-------------------------------------------------------------------------------
# Operation


class Operation(ListWrapper):
    '''Representation of a system operation.'''
    _attrs = dict(order = Attr(int, doc='An integer specifying the '
                               'order in which to perform the operation '
                               '(smaller values are performed earlier)'),
                  repetitions = Attr(int, 0, doc='Number of times to repeat '
                                     'the operation'))
    _opts = dict(init_validate = True)

    order_offset = 0

    @init_hook
    def _adjust_order(self):
        self.order += self.order_offset

    @classmethod
    def optimize(cls, ops):
        ops.sort(key=attrgetter('order'))

        k = 0
        while k < len(ops) - 1:
            ops[k].reduce(ListView(ops, k+1, -1))
            k += 1

    def combine(self, other):
        '''Combine with another operation to increase execution efficiency.'''
        raise NotImplementedError

    def execute(self):
        '''Execute the operation on the system'''
        raise NotImplementedError

    def _reduce_single(self, op, ops):
        self.combine(op)

    def reduce(self, ops):
        '''Reduce a list of operations for optimizing total execution'''
        N = len(ops)
        while ops:
            op = ops[0]
            if not subclass_equivalent(self, op):
                break
            
            self._reduce_single(op, ops)
            if N == len(ops):
                break
            N = len(ops)
            

#-------------------------------------------------------------------------------
# Independent Operation


class Independent(Operation):
    '''An independent operation that cannot be combined with others.'''

    def combine(self, other):
        '''Combine does nothing, because operations are independent.'''
        pass

#-------------------------------------------------------------------------------
# Combinable Operation


class Combinable(Operation):
    '''An operation that can be combined with others of like type.'''

    def combine(self, other):
        '''Adds the operational parameters of other to our own.'''
        self.extend(other)

    def _reduce_single(self, op, ops):
        super(Combinable, self)._reduce_single(op, ops)
        ops.pop(0)

#-------------------------------------------------------------------------------
# Idempotent Operation


class Idempotent(Combinable):
    '''An operation for which repeated executions has no meaningful effect.'''

    def combine(self, other):
        '''Does nothing, because repeating the execution is not meaningful.'''
        pass

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Operation', 'Independent', 'Combinable', 'Idempotent',
           'subclass_equivalent', 'ListView')

#-------------------------------------------------------------------------------
