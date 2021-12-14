def pytest_addoption(parser):
    parser.addoption("--metacls", action="store", default="")
