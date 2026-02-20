from __future__ import annotations

__version__ = "0.0.3"
# pylst/__init__.py
"""
pylst
=====

A Python package for processing, analyzing and visualizing Landsat-derived
Land Surface Temperature (LST) data.
"""


# ─── Core ────────────────────────────────────────────────────────────────
from .algorithms import LSTAlgorithmRunner

# ─── LST & Emissivity Computation ────────────────────────────────────────
from .pylst import emissivity

# ─── Utilities & Indices ─────────────────────────────────────────────────
from .utils import (
    generate_mask,
    compute_ndvi,
    fractional_vegetation_cover,
    cavity_effect,
    rescale_band,
)

# ─── Data Access & I/O ───────────────────────────────────────────────────
from .open import (
    remopener,
    download_images,
)

# ─── Visualization ───────────────────────────────────────────────────────
from .visualization import (
    rastshow)

# ─── Spatial Analysis ────────────────────────────────────────────────────
# spatial_analysis has extra dependencies (e.g. geopandas) that are not
# always required by users of the core library. Import lazily so that
# installing pylst doesn't force geopandas installation for everyone.
try:
    from .spatial_analysis.zonstat import calculate_zs
    from .spatial_analysis.changedet import analyze_images
except ImportError:  # pragma: no cover - optional dependency
    calculate_zs = None  # type: ignore
    analyze_images = None  # type: ignore

# ─── Normalization ───────────────────────────────────────────────────────
from .normalization import nrs


# ─── Public API ──────────────────────────────────────────────────────────
__all__ = [
    "LSTAlgorithmRunner",
    "emissivity",
    "generate_mask",
    "compute_ndvi",
    "fractional_vegetation_cover",
    "cavity_effect",
    "rescale_band",
    "remopener",
    "download_images",
    "rastshow",
    "histogram_equalization",
    "calculate_zs",
    "analyze_images",
    "nrs",

]
