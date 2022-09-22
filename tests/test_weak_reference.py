import copy
import pickle

import pytest  # noqa

from basicco.weak_reference import UniqueHashWeakReference, WeakReference


class Cls(object):
    pass


def test_empty_weak_reference():
    weak = WeakReference()
    assert weak() is None


def test_weak_reference():
    strong = Cls()
    strong_hash = hash(strong)
    weak_a = WeakReference(strong)
    weak_b = WeakReference(strong)
    assert weak_a() is strong
    assert weak_b() is strong
    assert hash(weak_a) == strong_hash
    assert hash(weak_b) == strong_hash
    assert weak_a == weak_b
    del strong
    assert weak_a() is None
    assert weak_b() is None
    assert hash(weak_a) == strong_hash
    assert hash(weak_b) == strong_hash
    assert weak_a == weak_b


def test_pickling():
    strong = Cls()
    weak = WeakReference(strong)
    unpickled_strong, unpickled_weak = pickle.loads(pickle.dumps((strong, weak)))
    assert isinstance(unpickled_strong, Cls)
    assert isinstance(unpickled_weak, WeakReference)
    assert unpickled_weak() is unpickled_strong
    assert type(pickle.loads(pickle.dumps(weak()))) is Cls


def test_caching():
    x = Cls()
    z = Cls()
    xr = WeakReference(x)
    zr = WeakReference(z)
    xr2 = WeakReference(x)
    zr2 = WeakReference(z)
    nr = WeakReference()
    nr2 = WeakReference()

    assert xr is xr2
    assert zr is zr2
    assert nr is nr2

    del z

    _x, _xr, _zr, _xr2, _zr2, _nr, _nr2 = pickle.loads(pickle.dumps((x, xr, zr, xr2, zr2, nr, nr2)))

    assert _xr is _xr2
    assert _zr is _zr2
    assert _nr is _nr2
    assert _nr is nr
    assert _nr2 is nr2
    assert _nr2 is nr
    assert _nr is nr2

    assert _xr() is _x
    assert _xr2() is _x


def test_deepcopy():
    x = Cls()
    z = Cls()
    xr = WeakReference(x)
    zr = WeakReference(z)
    xr2 = WeakReference(x)
    zr2 = WeakReference(z)
    nr = WeakReference()
    nr2 = WeakReference()

    assert xr is xr2
    assert zr is zr2
    assert nr is nr2

    del z

    _x, _xr, _zr, _xr2, _zr2, _nr, _nr2 = copy.deepcopy((x, xr, zr, xr2, zr2, nr, nr2))

    assert _xr is _xr2
    assert _zr is _zr2
    assert _nr is _nr2
    assert _nr is nr
    assert _nr2 is nr2
    assert _nr2 is nr
    assert _nr is nr2

    assert _xr() is _x
    assert _xr2() is _x


def test_hashing():
    class Unhashable(object):
        __hash__ = None

    unhashable = Unhashable()
    unhashable_ref = WeakReference(unhashable)
    hashable_ref = UniqueHashWeakReference(unhashable)

    assert unhashable_ref is not hashable_ref

    with pytest.raises(TypeError):
        hash(unhashable_ref)

    assert hash(hashable_ref) == object.__hash__(hashable_ref)

    assert WeakReference() is not UniqueHashWeakReference()


if __name__ == "__main__":
    pytest.main()
