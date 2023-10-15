"""Tests for the acyclic_toposrt module."""

import pytest

from cyclic_toposort.acyclic_toposort import acyclic_toposort


def test_runtimeerror_acyclic_toposort() -> None:
    """Test acyclic_toposort with a cyclic graph, expecting a cyclic graph RuntimeError."""
    edges = {(1, 2), (2, 3), (3, 1)}
    with pytest.raises(RuntimeError, match="Cyclic graph detected in acyclic_toposort function"):
        acyclic_toposort(edges)
