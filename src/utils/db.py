# Small cross-cutting DB helper.

from typing import TypeVar

T = TypeVar("T")


def require_id(model_id: T | None) -> T:
    """
    Narrows a SQLModel row's Optional primary key to its non-Optional
    type, for callers who already know -- from having just fetched or
    created-and-committed the row -- that it's populated. SQLModel
    types every primary key as Optional (e.g. `id: int | None`)
    because it's genuinely None only before the first INSERT, a
    distinction Pyright can't express from the annotation alone.

    Raises rather than silently asserting, so a real bug (passing an
    unpersisted row where a persisted one was assumed) fails loudly
    with a clear message instead of an obscure error somewhere downstream.
    """
    if model_id is None:
        raise ValueError("Expected a persisted row's primary key, got None.")
    return model_id
