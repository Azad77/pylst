# pylst/spatial_analysis/__init__.py
"""
Spatial analysis submodule for pylst.

Provides tools for:
- Change detection between raster images (analyze_images)
- Zonal statistics (summarize raster values within vector zones) (calculate_zs)

These functions are useful for post-processing LST results, such as:
- Detecting urban expansion impacts on temperature
- Computing average LST per administrative district or land-use polygon
"""

# spatial analysis functions rely on geopandas, import lazily
try:
    from .changedet import analyze_images
    from .zonstat import calculate_zs
except ImportError:  # pragma: no cover - optional dependency
    analyze_images = None  # type: ignore
    calculate_zs = None  # type: ignore

__all__ = [
    "analyze_images",
    "calculate_zs",
]