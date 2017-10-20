import yaml
import shlex
from . import globals as globs
from syn.five import STR
from syn.type import AnyType
from functools import partial
from operator import attrgetter
from subprocess import Popen, PIPE
from syn.type import List, Mapping
from syn.base_utils import AttrDict
from syn.base import Base, Attr, create_hook
from .operation import Operation
from .relation import Relation, Eq

#-------------------------------------------------------------------------------
# Utilities

OAttr = partial(Attr, optional=True)

def command(cmd, capture_output=False, returncode=False, silent=None):
    if silent is None:
        silent = not globs.print_command
    if not silent:
        print(cmd)
    args = shlex.split(cmd)
    kwargs = {}
    if capture_output:
        kwargs['stdout'] = PIPE
        kwargs['stderr'] = PIPE
    p = Popen(args, **kwargs)
    out, err = p.communicate()
    if returncode:
        return p.returncode
    out = out.decode('utf-8') if out else ''
    if capture_output:
        return out
    return out, p.returncode

output = partial(command, capture_output=True, silent=True)
status = partial(command, returncode=True, silent=True)

#-----------------------------------------------------------
# Order cache

DEPENDENCY_ORDERS = AttrDict()

#-----------------------------------------------------------
# Key cache

DEPENDENCY_KEYS = dict()

#-------------------------------------------------------------------------------
# Dependency


class Dependency(Base):
    '''Basic representation of a dependency'''
    _pkgs = dict()
    key = None
    order = 10000

    _attrs = dict(name = Attr(STR),
                  version = Attr(Relation, init=lambda self: Relation(),
                                 doc='Version relation for this dependency'),
                  always_upgrade = Attr(bool, default=False,
                                        doc='Always attempt to upgrade'),
                  order = Attr(int, default = order, internal = True))
    _opts = dict(init_validate = True,
                 optional_none = True,
                 make_hashable = True,
                 args = ('name', 'version'))

    @classmethod
    @create_hook
    def _register_info(cls):
        if cls.key:
            DEPENDENCY_KEYS[cls.key] = cls
            DEPENDENCY_ORDERS[cls.key] = cls.order

    @classmethod
    def from_conf(cls, obj):
        if isinstance(obj, STR):
            ver = Relation.dispatch(obj)
            return cls(ver.name, ver)

        if not isinstance(obj, dict):
            raise TypeError("Invalid object: {}".format(obj))

        if not len(obj) == 1:
            raise TypeError("Invalid dict: {}".format(obj))

        name = list(obj.keys())[0]
        kwargs = obj[name]
        kwargs['name'] = name
        if 'version' not in kwargs:
            ver = Relation.dispatch(name)
            kwargs['name'] = ver.name
            kwargs['version'] = ver
        else:
            kwargs['version'] = Eq.dispatch(str(kwargs['version']))
        return cls(**kwargs)

    def check(self):
        '''Returns True if the dependency is satisfied, False otherwise.'''
        if self.installed():
            if self.version(self._pkgs[self.name]):
                return True
        return False

    def export(self):
        return self.name + self.version.emit()

    def installed(self):
        return self.name in self._pkgs

    def satisfy(self):
        '''Satisfies the dependency if currently unsatisfied.'''
        raise NotImplementedError


#-------------------------------------------------------------------------------
# Depedencies


class Dependencies(Base):
    '''Representation of the various dependency sets'''
    special_contexts = ('includes',)

    _attrs = dict(contexts = Attr(Mapping(List(Dependency), AttrDict),
                                  init=lambda x: AttrDict(),
                                  doc='Diction of dependencies in their '
                                  'various contexts'),
                  includes = Attr(Mapping(List(STR), AttrDict),
                                  init=lambda x: AttrDict(),
                                  doc='Specification of which contexts to '
                                  'include in others'))
    _opts = dict(init_validate = True,
                 coerce_args = True)

    @classmethod
    def _contexts(cls, dct):
        return [key for key in dct if key not in cls.special_contexts]

    @classmethod
    def _from_context(cls, dct):
        deps = []
    
        for key in dct:
            typ = DEPENDENCY_KEYS[key]
            deps.extend([typ.from_conf(obj) for obj in dct[key]])

        deps.sort(key=attrgetter('order'))
        return deps

    @classmethod
    def from_yaml(cls, fil):
        dct = yaml.load(fil)
        contexts = cls._contexts(dct)
        includes = dct.get('includes', {})
        contexts = {context: cls._from_context(dct.get(context, {}))
                    for context in contexts}
        kwargs = dict(contexts = AttrDict(contexts),
                      includes = AttrDict(includes))
        return cls(**kwargs)

    def contexts_from_includes(self, context, contexts):
        new = self.includes.get(context, [])

        if new:
            contexts.extend(list(filter(lambda c: c not in contexts, new)))
            for con in new:
                self.contexts_from_includes(con, contexts)

    def deps_from_context(self, context):
        contexts = [context]
        if context == 'all':
            contexts = self.contexts
        elif context not in self.contexts:
            raise ValueError('Invalid context: {}'.format(context))

        self.contexts_from_includes(context, contexts)

        ret = []
        for con in contexts:
            ret += getattr(self.contexts, con)
        ret.sort(key=attrgetter('order'))
        return ret

    def satisfy(self, context, deptype=None, execute=True):
        if deptype is None:
            deptype = AnyType()

        ops = []
        for dep in self.deps_from_context(context):
            if deptype.query(dep):
                ops.extend(dep.satisfy())

        Operation.optimize(ops)
        if execute:
            for op in ops:
                op.execute()
        return ops

    def export_header(self):
        from . import __version__ as ver
        return '# Auto-generated by depman {}\n'.format(ver)

    def export(self, context, deptype, outfile, write=True, include_header=True):
        deps = [dep for dep in self.deps_from_context(context) 
                if deptype.query(dep)]

        out = ''
        if include_header:
            out = self.export_header()
        exports = sorted([dep.export() for dep in deps])
        out += '\n'.join(exports)
        
        if write:
            outfile.write(out)
        return out

    def validate(self):
        super(Dependencies, self).validate()
        
        for key, value in self.includes.items():
            assert key in self.contexts, \
                "Each key ({}) in includes must be a valid context".format(key)
            
            for con in value:
                assert con in self.contexts, \
                    "Each list item ({}) must be a valid context".format(con)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Dependency', 'Dependencies', 'command', 'status')

#-------------------------------------------------------------------------------
