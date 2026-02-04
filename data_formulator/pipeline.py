"""Utilities for managing transformation pipelines.

This module contains the :class:`TransformationPipeline` which coordinates
sequential record processing via simple callables.  Historically the
constructor used a mutable list as the default value for ``steps``.  That
meant that pipelines created without explicit steps would accidentally share
state which is a serious foot-gun when building reusable flows.  The
constructor now defensively copies user supplied iterables and defaults to
``None`` which avoids the shared-state bug while keeping the API simple.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class TransformationPipeline:
    """Apply a sequence of callables to a value.

    Parameters
    ----------
    steps:
        Optional iterable of callables that each accept a single argument and
        return the transformed value.  The iterable is eagerly copied so that
        subsequent mutations to the user supplied sequence do not leak into the
        pipeline.
    """

    _steps: List[Callable[[Any], Any]]

    def __init__(
        self,
        steps: Optional[Iterable[Callable[[Any], Any]]] = None,
    ) -> None:
        copied_steps: List[Callable[[Any], Any]]
        if steps is None:
            copied_steps = []
        else:
            copied_steps = [*steps]
        self._steps = copied_steps

    def add_step(self, step: Callable[[Any], Any]) -> "TransformationPipeline":
        """Append a transformation step.

        ``step`` must be callable.  The method returns ``self`` to enable a
        fluent style which works well for simple, programmatic pipeline
        construction.
        """

        if not callable(step):  # pragma: no cover - defensive guard
            raise TypeError("Pipeline steps must be callable")
        self._steps.append(step)
        return self

    @property
    def steps(self) -> tuple[Callable[[Any], Any], ...]:
        """Read-only view of the configured steps."""

        return tuple(self._steps)

    def run(self, value: Any) -> Any:
        """Run ``value`` through the configured pipeline."""

        result = value
        for step in self._steps:
            result = step(result)
        return result

    def clone(self) -> "TransformationPipeline":
        """Return a shallow copy of the pipeline."""

        return TransformationPipeline(self._steps)
