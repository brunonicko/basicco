import pickle

import pytest  # noqa
import six
from tippo import Type

from basicco.dynamic_class import make_cls
from basicco.obj_state import Reducible, ReducibleMeta


class MetaClass(ReducibleMeta):
    pass


class BaseClass(six.with_metaclass(ReducibleMeta, Reducible)):
    foo = None


class ParentClass(object):
    pass


def test_make_cls():
    cls = make_cls(
        "ParentClass.MyClass",
        bases=(BaseClass,),
        meta=MetaClass,
        dct={"foo": "bar"},
    )  # type: Type[BaseClass]
    ParentClass.MyClass = cls

    assert cls is ParentClass.MyClass
    assert cls.__name__ == "MyClass"
    assert cls.__qualname__ == "ParentClass.MyClass"
    assert cls.__module__ == __name__
    assert cls.foo == "bar"
    assert issubclass(cls, BaseClass)
    assert isinstance(cls, MetaClass)
    assert type(pickle.loads(pickle.dumps(cls()))) is cls


if __name__ == "__main__":
    pytest.main()
