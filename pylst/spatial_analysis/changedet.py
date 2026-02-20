# pylst/spatial_analysis/changedet.py
"""
Change detection utilities for raster data (e.g. LST, NDVI, land cover) in pylst.

Main function:
- analyze_images(): Compute difference/ratio/change map between two rasters and save result.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Literal, Optional, Tuple

import numpy as np
import rasterio
from numpy.typing import NDArray
from rasterio import Affine


ChangeMethod = Literal["difference", "ratio", "normalized_difference"]


def analyze_images(
    image_path1: str | Path,
    image_path2: str | Path,
    output_path: str | Path,
    method: ChangeMethod = "difference",
    band: int = 1,
    threshold: Optional[float] = None,
    nodata_value: Optional[float] = None,
) -> dict[str, NDArray | None]:
    """
    Perform change detection between two raster images (e.g. LST at t1 and t2).

    Computes one of:
    - "difference":      image2 - image1
    - "ratio":           image2 / image1
    - "normalized_difference": (image2 - image1) / (image2 + image1)

    Optionally applies a threshold to create a binary change mask.

    Args:
        image_path1, image_path2: Paths to input GeoTIFF files (earlier and later time)
        output_path: Where to save the change map as GeoTIFF
        method: Type of change metric ("difference", "ratio", "normalized_difference")
        band: Band number to read (default 1, for single-band LST)
        threshold: Optional value; pixels with absolute change >= threshold → marked as change
        nodata_value: Optional nodata value to mask in input rasters

    Returns:
        Dictionary with:
        - "change_map": computed change array
        - "binary_change": binary mask if threshold provided (1=change, 0=no change)
        - "metadata": rasterio metadata of output

    Raises:
        ValueError: mismatched CRS, shape, or band
        FileNotFoundError: input file missing
    """
    image_path1 = Path(image_path1)
    image_path2 = Path(image_path2)
    output_path = Path(output_path)

    for p in (image_path1, image_path2):
        if not p.is_file():
            raise FileNotFoundError(f"Input raster not found: {p}")

    with rasterio.open(image_path1) as src1, rasterio.open(image_path2) as src2:
        # Validate compatibility
        if src1.crs != src2.crs:
            warnings.warn("Input rasters have different CRS → reproject if needed", UserWarning)

        if src1.shape != src2.shape:
            raise ValueError(f"Shape mismatch: {src1.shape} vs {src2.shape}")

        if band < 1 or band > src1.count or band > src2.count:
            raise ValueError(f"Band {band} not available (max: {src1.count})")

        # Read data
        data1 = src1.read(band).astype(np.float64)
        data2 = src2.read(band).astype(np.float64)

        # Apply nodata masking
        if nodata_value is not None:
            data1[data1 == nodata_value] = np.nan
            data2[data2 == nodata_value] = np.nan
        else:
            data1 = np.where(np.isfinite(data1), data1, np.nan)
            data2 = np.where(np.isfinite(data2), data2, np.nan)

        # Compute change
        if method == "difference":
            change = data2 - data1
        elif method == "ratio":
            change = np.divide(data2, data1, where=(data1 != 0), out=np.full_like(data1, np.nan))
        elif method == "normalized_difference":
            denom = data2 + data1
            change = np.divide(data2 - data1, denom, where=(denom != 0), out=np.full_like(data1, np.nan))
        else:
            raise ValueError(f"Unknown method: {method}. Choose 'difference', 'ratio', or 'normalized_difference'")

        # Optional binary change mask
        binary_change = None
        if threshold is not None:
            binary_change = np.abs(change) >= threshold
            binary_change = binary_change.astype(np.uint8)  # 0/1

        # Prepare output metadata
        meta = src1.meta.copy()
        meta.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            nodata=np.nan,
        )

        # Save result
        with rasterio.open(output_path, "w", **meta) as dst:
            dst.write(change.astype(np.float32), 1)

        return {
            "change_map": change,
            "binary_change": binary_change,
            "metadata": meta,
        }