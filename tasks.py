import sys
import functools
from invoke import task  # type: ignore

PY_VERSION = sys.version_info[:2]


def requires_python(*python):
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if PY_VERSION < python:
                error = "can't run {!r} task in python {}".format(func.__name__, python_version)
                raise RuntimeError(error)
            return func(*args, **kwargs)
        return wrapped
    return decorator


@task
@requires_python(2, 7)
def tests(c):
    c.run("python -m pytest -vv -rs tests")
    c.run("python -m pytest --doctest-modules -vv -rs README.rst")


@task
@requires_python(3, 10)
def docs(c):
    c.run("sphinx-build -M html ./docs/source ./docs/build")


@task
@requires_python(3, 10)
def mypy(c):
    c.run("mypy basicco")


@task
@requires_python(3, 10)
def lint(c):
    c.run("flake8 basicco --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run("flake8 tests --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run(
        "flake8 basicco --count --ignore=F403,F401,E203,E731,C901,W503,F811 "
        "--max-line-length=120 --statistics"
    )
    c.run(
        "flake8 tests --count --ignore=F403,F401,E203,E731,C901,W503,F811 "
        "--max-line-length=120 --statistics"
    )


@task
@requires_python(3, 10)
def black(c):
    c.run("black basicco --line-length=120")
    c.run("black tests --line-length=120")


@task
@requires_python(3, 10)
def checks(c):
    black(c)
    lint(c)
    mypy(c)
    tests(c)
    docs(c)
