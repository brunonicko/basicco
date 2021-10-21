import os
import sys

if sys.version_info[0:2] < (3, 9):
    error = (
        "Python 3.9+ is required for development tasks, you are running {}\n"
    ).format(sys.version)
    sys.stderr.write(error)
    sys.exit(1)

from invoke import task  # type: ignore


@task
def docs(c):
    c.run(".{sep}docs{sep}make html".format(sep=os.sep))


@task
def tests(c):
    c.run("python -m pytest -vv -rs tests")


@task
def tox(c):
    c.run("tox")


@task
def mypy(c):
    c.run("mypy basicco")


@task
def lint(c):
    c.run("flake8 basicco --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run("flake8 tests --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run(
        "flake8 basicco --count --ignore=F403,F401,E203,E731,C901 "
        "--max-line-length=88 --statistics"
    )
    c.run(
        "flake8 tests --count --ignore=F403,F401,E203,E731,C901 "
        "--max-line-length=88 --statistics"
    )


@task
def black(c):
    c.run("black basicco")
    c.run("black tests")


@task
def checks(c):
    black(c)
    lint(c)
    mypy(c)
    tox(c)
