# Verifies utils/db.py::require_id() -- the helper used throughout the
# codebase to narrow a SQLModel row's Optional primary key to int once
# the row is known to be persisted.

import pytest

from utils.db import require_id


def test_require_id_returns_the_value_when_present():
    assert require_id(42) == 42


def test_require_id_raises_on_none():
    with pytest.raises(ValueError, match="Expected a persisted row's primary key"):
        require_id(None)
