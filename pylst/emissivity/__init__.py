# pylst/emissivity/__init__.py
"""
Emissivity estimation submodule for pylst.

Provides NDVI-based and mono-window methods to estimate land surface
emissivity (LSE) — critical for LST retrieval from Landsat TIRS.
"""

from __future__ import annotations

# ─── Algorithm classes ───────────────────────────────────────────────────────
from .algorithms import (
    ComputeMonoWindowEmissivity,
    ComputeEmissivityNBEM,
    ComputeEmissivityGopinadh,
    ComputeNDVIThresholdEmissivity,
)

# ─── Default algorithms dictionary ───────────────────────────────────────────
# Exposed so pylst.py can import it without errors
default_algorithms = {
    "mono-window": ComputeMonoWindowEmissivity,
    "nbem": ComputeEmissivityNBEM,
    "gopinadh": ComputeEmissivityGopinadh,
    "ndvi-threshold": ComputeNDVIThresholdEmissivity,
}

# ─── Core runner ─────────────────────────────────────────────────────────────
from .registry import emissivity_runner, EmissivityRunner

# ─── Public API ──────────────────────────────────────────────────────────────
__all__ = [
    "default_algorithms",
    "emissivity_runner",
    "EmissivityRunner",
    "ComputeMonoWindowEmissivity",
    "ComputeEmissivityNBEM",
    "ComputeEmissivityGopinadh",
    "ComputeNDVIThresholdEmissivity",
]
