from pytest import main

from basicco.utils.frozen_dict import FrozenDict


def test_frozen_dict():
    wrapped = {"bar": "foo"}
    frozen = FrozenDict(wrapped)

    wrapped["bar"] = "baz"
    assert frozen["bar"] == "foo"
    assert wrapped["bar"] == "baz"


if __name__ == "__main__":
    main()
