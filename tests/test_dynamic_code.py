import pytest  # noqa

from basicco.dynamic_code import (
    compile_and_eval,
    generate_unique_filename,
    make_function,
)


def test_generate_unique_filename():
    assert generate_unique_filename("my_func") == "<generated my_func>"
    assert generate_unique_filename("my_func", "module") == "<generated module.my_func>"
    assert generate_unique_filename("my_method", "module", "Class") == "<generated module.Class.my_method>"


def test_compile_and_eval():
    globs = {}
    compile_and_eval("foo = 40", globs)
    compile_and_eval("bar = 2", globs)
    compile_and_eval("foobar = foo + bar", globs)
    assert globs["foo"] == 40
    assert globs["bar"] == 2
    assert globs["foobar"] == 42


def test_make_function():
    name = "my_func"
    script = """
def my_func(foo=foo_default, bar=bar_default):
    return foo + bar
"""
    globs = {"foo_default": 1, "bar_default": 2}
    filename = generate_unique_filename("my_func", __name__)
    module = __name__
    my_func = make_function(name, script, globs, filename, module)

    assert my_func() == 3
    assert my_func(5, 5) == 10


if __name__ == "__main__":
    pytest.main()
