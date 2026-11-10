#!/usr/bin/env python3
"""Compatibility entry point for the dashboard application."""

from __future__ import annotations

import os
import sys

if __name__ == "__main__":
    import uvicorn

    from dashboard.backend.server import app

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("SCICODE_DASHBOARD_PORT", "8765")))
else:
    # Preserve `from dashboard import server` for callers and tests while the
    # implementation lives with the other backend modules.
    from dashboard.backend import server as _server

    sys.modules[__name__] = _server
