from .fares.models import *
from .reference.models import *


def create_all():
    from . import Base
    from .engine import sa_engine
    Base.metadata.create_all(sa_engine)

