"""Cache decorators that work both inside Streamlit and in the standalone API.

The Streamlit app caches with ``st.cache_data`` / ``st.cache_resource``. The
webapp FastAPI backend reuses these same ``lib`` modules but has no Streamlit
runtime, so it sets ``WEBAPP_API=1`` before importing ``lib`` and gets plain
``functools`` memoization instead. When the env var is unset (i.e. under
``streamlit run``) the decorators proxy to Streamlit unchanged, so the existing
app behaves exactly as before.

Both ``cache_data`` and ``cache_resource`` are usable bare (``@cache_data``) or
called (``@cache_data(ttl=...)``); any keyword arguments are accepted and
ignored in the standalone path. All cached callables here take only hashable
positional arguments, so ``lru_cache`` is a safe stand-in.
"""

from __future__ import annotations

import os
from functools import lru_cache


def _passthrough_cache(func=None, **_kwargs):
    """A Streamlit-free decorator usable as ``@cache`` or ``@cache(...)``."""

    def wrap(fn):
        return lru_cache(maxsize=None)(fn)

    if callable(func):
        return wrap(func)
    return wrap


if os.environ.get("WEBAPP_API") == "1":
    cache_data = _passthrough_cache
    cache_resource = _passthrough_cache
else:  # pragma: no cover - exercised only under `streamlit run`
    import streamlit as st

    cache_data = st.cache_data
    cache_resource = st.cache_resource
