from operator import attrgetter
from syn.base import ListWrapper, Attr, init_hook
from syn.base_utils import same_lineage, ListView

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
            if not same_lineage(self, op):
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

__all__ = ('Operation', 'Independent', 'Combinable', 'Idempotent')

#-------------------------------------------------------------------------------
