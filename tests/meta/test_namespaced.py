import pytest

from six import with_metaclass

from basicco import BaseMeta
from basicco.namespaced import NamespacedMeta
from basicco.utils.namespace import Namespace


@pytest.mark.parametrize("meta", (NamespacedMeta, BaseMeta))
def test_private_namespace(meta):
    class Class(with_metaclass(meta, object)):
        pass

    assert isinstance(Class._namespace, Namespace)

    class SubClassA(Class):
        pass

    assert isinstance(SubClassA._namespace, Namespace)

    class SubClassB(Class):
        pass

    assert isinstance(SubClassB._namespace, Namespace)

    class SubClassC(SubClassA, SubClassB):
        pass

    assert isinstance(SubClassC._namespace, Namespace)

    namespace_ids = {
        id(Class._namespace),
        id(SubClassA._namespace),
        id(SubClassB._namespace),
        id(SubClassC._namespace),
    }

    assert len(namespace_ids) == 4


if __name__ == "__main__":
    pytest.main()
