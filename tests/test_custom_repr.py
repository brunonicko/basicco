import pytest  # noqa

from basicco.custom_repr import iterable_repr, mapping_repr


def test_custom_mapping_repr():
    mapping = {1: 4, "2": 3, 3: 2, "4": "1"}
    assert (
        mapping_repr(
            mapping,
            prefix="Mapping<",
            template="{key}=={value}",
            separator="; ",
            suffix=">",
            sorting=True,
            sort_key=lambda i: str(i[1]),
            reverse=True,
            key_repr=lambda k: repr("K" + str(k)),
            value_repr=lambda v: str("V" + str(v)),
        )
        == "Mapping<'K1'==V4; 'K2'==V3; 'K3'==V2; 'K4'==V1>"
    )

    items = ((1, 4), ("2", 3), (3, 2), ("4", "1"))
    assert (
        mapping_repr(
            items,
            prefix="Items:\n",
            template="    [{i}] {key: <3}: {value}",
            separator="\n",
            suffix="",
        )
        == """Items:
    [0] 1  : 4
    [1] '2': 3
    [2] 3  : 2
    [3] '4': '1'"""
    )


def test_custom_iterable_repr():
    iterable = ["a", 1, 2.0, "3.0", 4, None]
    assert iterable_repr(iterable) == repr(iterable)
    assert (
        iterable_repr(
            iterable,
            prefix="Iterable -",
            template=lambda i, value: "> {i}:{value} <".format(i=i, value=value),
            separator="-",
            suffix="-",
            sorting=True,
            sort_key=lambda v: str(v),
            reverse=True,
            value_repr=lambda v: str("V" + str(v)),
        )
        == "Iterable -> 0:Va <-> 1:VNone <-> 2:V4 <-> 3:V3.0 <-> 4:V2.0 <-> 5:V1 <-"
    )


if __name__ == "__main__":
    pytest.main()
