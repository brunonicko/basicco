import pytest

from basicco.namespace import MutableNamespace, NamespacedMeta


def test_private_namespace():
    class Class(metaclass=NamespacedMeta):
        pass

    assert isinstance(Class.__namespace__, MutableNamespace)

    class SubClassA(Class):
        pass

    assert isinstance(SubClassA.__namespace__, MutableNamespace)

    class SubClassB(Class):
        pass

    assert isinstance(SubClassB.__namespace__, MutableNamespace)

    class SubClassC(SubClassA, SubClassB):
        pass

    assert isinstance(SubClassC.__namespace__, MutableNamespace)

    namespace_ids = {
        id(Class.__namespace__),
        id(SubClassA.__namespace__),
        id(SubClassB.__namespace__),
        id(SubClassC.__namespace__),
    }

    assert len(namespace_ids) == 4


if __name__ == "__main__":
    pytest.main()
