import pytest


@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    class FakePickle(object):
        def __init__(self):
            self.v = None

        def loads(self, v):
            return self.v

        def dumps(self, v):
            self.v = v

    doctest_namespace["pickle"] = FakePickle()
