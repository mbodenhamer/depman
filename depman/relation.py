'''Relations for package versions.'''
import operator as op
from syn.base import Base, Attr, create_hook

#-------------------------------------------------------------------------------

RELATION_CACHE = dict()

#-------------------------------------------------------------------------------
# Relation


class Relation(Base):
    _attrs = dict(rhs = Attr(str, default='',
                             doc='The value on the right hand side'))
    _opts = dict(init_validate = True,
                 make_hashable = True,
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
                name, rhs = s.split(key)
                return rel(rhs.strip(), name=name.strip())
        return cls('', name=s)

    def emit(self):
        repr = self.repr if self.repr else ''
        return repr + self.rhs


#-------------------------------------------------------------------------------
# Relations


class Eq(Relation):
    func = op.eq
    repr = '=='

    @classmethod
    def dispatch(cls, s):
        if any(val in s for val in RELATION_CACHE):
            return super(Eq, cls).dispatch(s)
        return cls(s)


class Eq_single(Eq):
    repr = '='


class Le(Relation):
    func = op.le
    repr = '<='


class Ge(Relation):
    func = op.ge
    repr = '>='


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Relation', 'Eq', 'Le', 'Ge')

#-------------------------------------------------------------------------------
