'''Relations for package versions.'''
import operator as op
from syn.base import Base, Attr, create_hook

#-------------------------------------------------------------------------------

RELATION_CACHE = dict()

#-------------------------------------------------------------------------------
# Relation


class Relation(Base):
    _attrs = dict(rhs = Attr(str, doc='The value on the right hand side of'
                             'the relation'))
    _opts = dict(coerce_args = True,
                 args = ('rhs',))

    func = None
    repr = None

    def __call__(self, value):
        if self.func is not None:
            return self.func(str(value), self.rhs)
        return True

    @classmethod
    @create_hook
    def _register(cls):
        if cls.repr is not None:
            RELATION_CACHE[cls.repr] = cls

    @classmethod
    def dispatch(cls, s):
        # Make sure the longer reprs get tested first
        for key, rel in sorted(RELATION_CACHE.items(), 
                               key=lambda x: -len(x[0])):
            if key in s:
                _, rhs = s.split(key)
                return rel(rhs)
        return cls('')


#-------------------------------------------------------------------------------
# Relations


class Eq(Relation):
    func = op.eq
    repr = '=='


class Lt(Relation):
    func = op.lt
    repr = '<'


class Le(Relation):
    func = op.le
    repr = '<='


class Gt(Relation):
    func = op.gt
    repr = '>'


class Ge(Relation):
    func = op.ge
    repr = '>='


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Relation', 'Eq', 'Lt', 'Le', 'Gt', 'Ge')

#-------------------------------------------------------------------------------
