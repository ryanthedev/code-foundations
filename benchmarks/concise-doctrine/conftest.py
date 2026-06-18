"""Root pytest config for the concise-doctrine benchmark.

Registers the `live` marker (real headless build runs that cost money) and gates
those tests behind an explicit `--run-live` flag so the default suite stays free,
deterministic, and CI-safe.
"""


def pytest_addoption(parser):
    parser.addoption(
        "--run-live", action="store_true", default=False,
        help="run the live end-to-end build tests (real `claude` subprocess, costs money)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live: real headless build (opt in with --run-live)"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        return
    import pytest

    skip_live = pytest.mark.skip(reason="needs --run-live")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
