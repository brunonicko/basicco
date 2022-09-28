import os
import shutil

from invoke import task  # type: ignore  # noqa


@task
def conform(c):
    c.run("isort basicco tests ./docs/source/conf.py setup.py tasks.py -m 3 -l 88 --up --tc --lbt 0 --color")
    c.run("black basicco --line-length=120")
    c.run("black tests --line-length=120")
    c.run("black setup.py --line-length=120")
    c.run("black tasks.py --line-length=120")


@task
def lint(c):
    c.run("flake8 basicco --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run("flake8 tests --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run(
        "flake8 basicco --count --ignore=F811,F405,F403,F401,E203,E731,C901,W503 " "--max-line-length=120 --statistics"
    )
    c.run("flake8 tests --count --ignore=F811,F405,F403,F401,E203,E731,C901,W503 " "--max-line-length=120 --statistics")


@task
def mypy(c):
    c.run("mypy basicco")


@task
def tests(c):
    c.run("python -m pytest -vv -rs tests")
    c.run("python -m pytest --doctest-modules -vv -rs README.rst")


@task
def docs(c):
    api_docs = "./docs/source/api"
    if os.path.exists(api_docs):
        assert os.path.isdir(api_docs), "not a directory: {!r}".format(api_docs)
        shutil.rmtree(api_docs)
    os.mkdir(api_docs)
    c.run("sphinx-apidoc basicco " "--separate " "--module-first " "--no-toc " "--output-dir {}".format(api_docs))
    c.run("sphinx-build -M html ./docs/source ./docs/build")
    shutil.rmtree(api_docs)


@task
def checks(c):
    conform(c)
    lint(c)
    mypy(c)
    tests(c)
    docs(c)
