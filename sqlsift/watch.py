"""Watch mode: re-run a query diff on a schedule and report changes."""

import time
import logging
from typing import Callable, Optional

from sqlsift.runner import compare_environments
from sqlsift.diff import DiffResult, is_equal

logger = logging.getLogger(__name__)


class WatchError(Exception):
    """Raised when watch mode encounters a fatal error."""


def _default_on_change(result: DiffResult, iteration: int) -> None:
    """Default callback: log a warning when a change is detected."""
    logger.warning(
        "[watch] iteration=%d status=CHANGED added=%d removed=%d",
        iteration,
        len(result.added),
        len(result.removed),
    )


def _default_on_stable(result: DiffResult, iteration: int) -> None:
    """Default callback: log info when results are stable."""
    logger.info("[watch] iteration=%d status=STABLE", iteration)


def watch(
    config: dict,
    env_a: str,
    env_b: str,
    query: str,
    interval: float = 30.0,
    max_iterations: Optional[int] = None,
    on_change: Optional[Callable[[DiffResult, int], None]] = None,
    on_stable: Optional[Callable[[DiffResult, int], None]] = None,
) -> None:
    """Poll two environments repeatedly and invoke callbacks on diff changes.

    Args:
        config: Parsed config dict (from load_config).
        env_a: Name of the baseline environment.
        env_b: Name of the comparison environment.
        query: SQL query to execute on both environments.
        interval: Seconds to wait between polls.
        max_iterations: Stop after this many iterations (None = run forever).
        on_change: Called when results differ; receives (DiffResult, iteration).
        on_stable: Called when results are identical; receives (DiffResult, iteration).
    """
    if interval <= 0:
        raise WatchError("interval must be a positive number")

    _on_change = on_change or _default_on_change
    _on_stable = on_stable or _default_on_stable

    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        iteration += 1
        try:
            result = compare_environments(config, env_a, env_b, query)
        except Exception as exc:  # noqa: BLE001
            raise WatchError(f"Query failed on iteration {iteration}: {exc}") from exc

        if is_equal(result):
            _on_stable(result, iteration)
        else:
            _on_change(result, iteration)

        if max_iterations is None or iteration < max_iterations:
            time.sleep(interval)
