from collections import OrderedDict
from .column import *


class AttrDict(dict):
    """A dictionary with attribute-style access. It maps attribute access to
    the real dictionary.  """

    def __init__(self, init={}):
        dict.__init__(self, init)

    def __getstate__(self):
        return self.__dict__.items()

    def __setstate__(self, items):
        for key, val in items:
            self.__dict__[key] = val

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))

    def __setitem__(self, key, value):
        return super(AttrDict, self).__setitem__(key, value)

    def __getitem__(self, name):
        return super(AttrDict, self).__getitem__(name)

    def __delitem__(self, name):
        return super(AttrDict, self).__delitem__(name)

    __getattr__ = __getitem__
    __setattr__ = __setitem__


def collect_current_columns(attrs):
    """ Collect fields/columns from current class. """
    current_columns = []
    for key, value in list(attrs.items()):
        if isinstance(value, Column):
            current_columns.append((key, value))
            del attrs[key]

    current_columns.sort(key=lambda x: x[1].creation_counter)
    attrs['declared_fields'] = OrderedDict(current_columns)

    return attrs


def assign_meta(new_class, bases, meta):
    m = {}
    for base in bases:
        m.update({k: v for k, v in getattr(base, "_meta", {}).items()})

    m.update({k: v for k, v in getattr(meta, "__dict__", {}).items() if not k.startswith("__")})
    _meta = AttrDict(m)

    return _meta


def filter_declared_fields(base, declared_fields):
    for attr, value in base.__dict__.items():
        if value is None and attr in declared_fields:
            del declared_fields[attr]
    return declared_fields


def define_declared_fields(new_class):
    declared_fields = OrderedDict()

    for base in reversed(new_class.__mro__):

        # Collect fields from base class.
        if hasattr(base, 'declared_fields'):
            declared_fields.update(base.declared_fields)

        # Field shadowing.
        declared_fields = filter_declared_fields(base, declared_fields)

    return declared_fields


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that collects Fields declared on the base classes.
    """
    def __new__(mcs, name, bases, attrs):

        # Pop the Meta class if exists
        meta = attrs.pop('Meta', None)

        attrs = collect_current_columns(attrs)

        new_class = (super(DeclarativeFieldsMetaclass, mcs).__new__(mcs, name, bases, attrs))

        _meta = assign_meta(new_class, bases, meta)

        # Walk through the MRO.
        declared_fields = define_declared_fields(new_class)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class._meta = _meta

        return new_class
