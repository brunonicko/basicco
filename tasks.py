import sys
from invoke import task  # type: ignore

PY_VERSION = sys.version_info[:2]


def require_python(*python):
    if PY_VERSION < python:
        error = "can't run {!r} task in python {}".format(func.__name__, PY_VERSION)
        raise RuntimeError(error)


@task
def black(c):
    require_python(3, 10)
    c.run("black basicco --line-length=120")
    c.run("black tests --line-length=120")


@task
def lint(c):
    require_python(3, 10)
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
def mypy(c):
    require_python(3, 10)
    c.run("mypy basicco")


@task
def tests(c):
    require_python(2, 7)
    c.run("python -m pytest -vv -rs tests")
    c.run("python -m pytest --doctest-modules -vv -rs README.rst")


@task
def docs(c):
    require_python(3, 10)
    c.run("sphinx-build -M html ./docs/source ./docs/build")


@task
def checks(c):
    require_python(3, 10)
    black(c)
    lint(c)
    mypy(c)
    tests(c)
    docs(c)
