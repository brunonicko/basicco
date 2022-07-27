from __future__ import absolute_import, division, print_function

import pytest  # noqa

from basicco.scrape_class import scrape_class


class Member(object):
    @staticmethod
    def filter(_base, _member_name, member):
        return isinstance(member, Member)

    @staticmethod
    def override_filter(base, member_name, member, previous_member):
        if not isinstance(member, Member):
            raise TypeError(
                "'{}.{}' is not of type {!r}".format(base.__name__, member_name, type(previous_member).__name__)
            )
        return isinstance(previous_member, Member)

    @staticmethod
    def replacer(_base, _member_name, member):
        if isinstance(member, Member):
            return str(member)
        return member


_foo_member = Member()
_bar_member = Member()
_foo_override_member = Member()
_foobar_member = Member()


class BaseA(object):
    a = "a"
    foo = _foo_member


class BaseB(BaseA):
    b = "b"
    bar = _bar_member  # type: Member | None


class BaseC(BaseB):
    c = "c"
    foo = _foo_override_member
    bar = None
    foobar = _foobar_member


def test_default():
    assert scrape_class(object) == {}
    assert scrape_class(BaseA) == {"foo": _foo_member, "a": "a"}
    assert scrape_class(BaseB) == {"foo": _foo_member, "bar": _bar_member, "a": "a", "b": "b"}
    assert scrape_class(BaseC) == {
        "foo": _foo_override_member,
        "bar": None,
        "foobar": _foobar_member,
        "a": "a",
        "b": "b",
        "c": "c",
    }


def test_member_filter():
    assert scrape_class(object, Member.filter) == {}
    assert scrape_class(BaseA, Member.filter) == {"foo": _foo_member}
    assert scrape_class(BaseB, Member.filter) == {"foo": _foo_member, "bar": _bar_member}
    assert scrape_class(BaseC, Member.filter) == {"foo": _foo_override_member, "foobar": _foobar_member}


def test_override_member_filter():
    assert scrape_class(object, Member.filter, Member.override_filter) == {}
    assert scrape_class(BaseA, Member.filter, Member.override_filter) == {"foo": _foo_member}
    assert scrape_class(BaseB, Member.filter, Member.override_filter) == {"foo": _foo_member, "bar": _bar_member}
    with pytest.raises(TypeError) as exc_info:
        scrape_class(BaseC, Member.filter, Member.override_filter)
    assert str(exc_info.value) == "'BaseC.bar' is not of type 'Member'"


def test_member_replacer():
    assert scrape_class(object, Member.filter) == {}
    assert scrape_class(BaseA, Member.filter, member_replacer=Member.replacer) == {"foo": str(_foo_member)}
    assert scrape_class(BaseB, Member.filter, member_replacer=Member.replacer) == {
        "foo": str(_foo_member),
        "bar": str(_bar_member),
    }
    assert scrape_class(BaseC, Member.filter, member_replacer=Member.replacer) == {
        "foo": str(_foo_override_member),
        "foobar": str(_foobar_member),
    }


if __name__ == "__main__":
    pytest.main()
