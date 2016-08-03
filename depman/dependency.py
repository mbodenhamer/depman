import yaml
from syn.five import STR
from syn.type import List
from functools import partial
from operator import attrgetter
from subprocess import Popen, PIPE
from syn.base import Base, Attr, init_hook, create_hook

#-------------------------------------------------------------------------------
# Utilities

OAttr = partial(Attr, optional=True)

def command(cmd):
    print(cmd)
    p = Popen(cmd, stdout=PIPE, shell=True)
    return p.communicate()[0].decode('utf-8')

def status(cmd):
    p = Popen(cmd, stdout=PIPE, shell=True)
    p.communicate()
    return p.returncode

#-----------------------------------------------------------
# Key cache

DEPENDENCY_KEYS = dict()

#-------------------------------------------------------------------------------
# Dependency


class Dependency(Base):
    '''Basic representation of a dependency'''
    key = None

    _attrs = dict(name = Attr(STR),
                  order = Attr(int, default = 10000, internal = True))
    _opts = dict(init_validate = True,
                 optional_none = True,
                 args = ('name',))

    @classmethod
    @create_hook
    def _register_key(cls):
        if cls.key:
            DEPENDENCY_KEYS[cls.key] = cls

    @classmethod
    def from_conf(cls, obj):
        if isinstance(obj, STR):
            return cls(obj)

        if not isinstance(obj, dict):
            raise TypeError("Invalid object: {}".format(obj))

        if not len(obj) == 1:
            raise TypeError("Invalid dict: {}".format(obj))

        name = list(obj.keys())[0]
        kwargs = obj[name]
        kwargs['name'] = name
        return cls(**kwargs)

    def check(self):
        '''Returns True if the dependency is satisfied, False otherwise.'''
        raise NotImplementedError

    def satisfy(self):
        '''Satisfies the dependency if currently unsatisfied.'''
        raise NotImplementedError


#-----------------------------------------------------------
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


#-----------------------------------------------------------
# Pip


class Pip(Dependency):
    '''Representation of a pip dependency'''
    key = 'pip'
    freeze = dict()

    _attrs = dict(version = OAttr(STR, default='',
                                  doc='Minimum version required'),
                  always_upgrade = OAttr(bool, default=False,
                                         doc='Always attempt to upgrade'),
                  order = Attr(int, 3))

    @init_hook
    def _populate_freeze(self):
        cls = type(self)
        if not cls.freeze:
            pkgs = command('pip freeze')
            cls.freeze = dict([tuple(line.split('==')) 
                               for line in pkgs.split('\n') if line])

    def check(self):
        if self.name in self.freeze:
            if self.version: 
                if self.version <= self.freeze[self.name]:
                    return True
                else:
                    return False
            else:
                return True
        return False

    def satisfy(self):
        if not self.check() or self.always_upgrade:
            command('pip install --upgrade {}'.format(self.name))


#-------------------------------------------------------------------------------
# Depedencies


class Dependencies(Base):
    '''Representation of the various dependency sets'''
    contexts = ('dev', 'prod')

    _attrs = dict(dev = Attr(List(Dependency), init=lambda x: list(),
                             doc='List of development dependencies'),
                  prod = Attr(List(Dependency), init=lambda x: list(),
                              doc='List of production dependencies'),
                  )
    _opts = dict(init_validate = True)

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
        kwargs = {context: cls._from_context(dct.get(context, {}))
                  for context in cls.contexts}
        return cls(**kwargs)

    def deps_from_context(self, context):
        contexts = [context]
        if context == 'all':
            contexts = self.contexts
        elif context not in self.contexts:
            raise ValueError('Invalid context: {}'.format(context))

        ret = []
        for sc in contexts:
            ret += getattr(self, sc)
        ret.sort(key=attrgetter('order'))
        return ret

    def satisfy(self, context):
        for dep in self.deps_from_context(context):
            dep.satisfy()


#-------------------------------------------------------------------------------
