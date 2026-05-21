"""Coverage for ``python -m pykotmig`` entry."""

from __future__ import annotations

import runpy
from unittest.mock import patch


def test_run_module_as_main_invokes_cli() -> None:
    with patch("pykotmig.cli.main.main") as mock_main:
        runpy.run_module("pykotmig", run_name="__main__")
    mock_main.assert_called_once()
