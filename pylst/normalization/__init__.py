# pylst/normalization/__init__.py
"""
Normalization utilities for Landsat LST and related raster data.

Main functions:
- nrs()           – Normalized Ratio Scale (custom method from Rasul et al., 2017)
- min_max_normalize() – Standard min-max scaling [0,1] or custom range
- z_score_normalize() – Z-score standardization (mean=0, std=1)

These help make LST values comparable across different acquisition dates,
sensors, or atmospheric conditions.
"""

from .normalizer import nrs, min_max_normalize, z_score_normalize

__all__ = [
    "nrs",
    "min_max_normalize",
    "z_score_normalize",
]