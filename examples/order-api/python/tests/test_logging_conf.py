"""Cover ``configure_logging`` branches."""

from __future__ import annotations

import importlib
import logging

import pytest


@pytest.fixture
def cleared_root_handlers() -> None:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    yield
    # leave logging usable for other tests in same session
    if not root.handlers:
        logging.basicConfig(level=logging.INFO)


def test_configure_short_circuits_when_handlers_present(
    cleared_root_handlers: None,
) -> None:
    import order_api.logging_conf as lc

    importlib.reload(lc)
    lc.configure_logging()
    n1 = len(logging.getLogger().handlers)
    lc.configure_logging()
    n2 = len(logging.getLogger().handlers)
    assert n1 == n2 >= 1
