from .relation import *
from .operation import *
from .dependency import *
from .apt import *
from .pip import *

from syn.base_utils import harvest_metadata, delete
with delete(harvest_metadata, delete):
    harvest_metadata('metadata.yml')
